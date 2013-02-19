# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

import os
import time

import bpy
import mathutils
import bpy_extras.io_utils


def name_compat(name):
    if name is None:
        return 'None'
    else:
        return name.replace(' ', '_')


def write_shapes_file(  filepath, object, scene,
                EXPORT_APPLY_MODIFIERS=True,
                EXPORT_PATH_MODE='AUTO',
                ):
    """
    Basic write function. The context and options must be already set
    """

    def veckey3d(v):
        return round(v.x, 6), round(v.y, 6), round(v.z, 6)

    time1 = time.time()

    file = open(filepath, "w", encoding="utf8", newline="\n")
    fw = file.write

    # Initialize totals, these are updated each object
    totverts = totuvco = totno = 1
    vertIndex = -1

    face_vert_index = 1

    globalVerts = {}
    vertDict = {}

    copy_set = set()


    if object.type == 'MESH' and object.data.shape_keys:
    
        mesh = object.data
        mesh_verts = mesh.vertices[:]
        mesh_face_index = [(index, face) for index, face in enumerate(mesh.polygons)]
        mesh_shape_index = [(index, keyblock) for index, keyblock in enumerate(mesh.shape_keys.key_blocks)]
        
        if (len(mesh_face_index) + len(mesh_verts)):
            
            
            fw('%s' % mesh.name)
            fw('_dimensions = ')
            fw('[%f,%f,%f];\n\n' % (object.dimensions[0],object.dimensions[1],object.dimensions[2]))
            
            #this adds the slider control variables for the shapes in customizer
            for index, keyblock in mesh_shape_index:
            	if keyblock.name == mesh.shape_keys.reference_key.name:
            		continue
            	else:
                	fw('%s' % keyblock.name)
                	fw('_value = 0; //[0:100]\n\n')
            
              #uncomment to include original mesh vert positions (shouldn't be needed since basis shapekey will have this info)
#             fw('%s' % mesh.name)
#             fw('_original_points = [[')
#             print(mesh_verts)
#             for vertex in mesh_verts:
#                 if vertex.index != 0:
#                     fw(',')
#                 fw('%f,%f,%f]' % (vertex.co.x,vertex.co.y,vertex.co.z))
#             fw('];')

            fw('polyhedron(triangles = ')
            fw('%s' % mesh.name)
            fw('_triangles, points = ')
            fw('%s' % mesh.name)
            fw('_shapes_points);\n\n')
            


            fw('%s' % mesh.name)
            fw('_triangles = [')            
            for index, face in mesh_face_index:
                face_verts = face.vertices
                if index != 0:
                    fw(',')
                if len(face_verts) == 3:
                    fw('[%d,%d,%d]' % (face_verts[2], face_verts[1], face_verts[0]))
                else:
                    fw('[%d,%d,%d],[%d,%d,%d]' % (face_verts[2],face_verts[1],face_verts[0],face_verts[3],face_verts[2],face_verts[0]))
            fw('];\n\n')
            
            for index, keyblock in mesh_shape_index:
                shape_verts_index = [(index, shape_vertex) for index, shape_vertex in enumerate(keyblock.data)]
                fw('%s' % mesh.name)
                fw('_')
                fw('%s' % keyblock.name)
                fw('_points = [')
                for index, vertex in shape_verts_index:
                    if index != 0:
                        fw(',')
                    fw('[%f,%f,%f]' % (vertex.co.x,vertex.co.y,vertex.co.z))
                fw('];\n\n')
            


            fw('%s' % mesh.name)
            fw('_shapes_points = [')
            for vertex in mesh_verts:
                if vertex.index != 0:
                    fw(',')
                fw('[')
                for com_index, component in enumerate(vertex.co):
                    if com_index != 0:
                        fw(',')
                    for key_index, keyblock in mesh_shape_index:
                        if key_index != 0:
                            fw('+')
                        if keyblock.name == mesh.shape_keys.reference_key.name:
                            fw('%s' % mesh.name)
                            fw('_')
                            fw('%s' % keyblock.name)
                            fw('_points[')
                            fw('%d]' % vertex.index)
                            fw('[%d]' % com_index)
                        else:
                            fw('((')
                            fw('%s' % mesh.name)
                            fw('_')
                            fw('%s' % keyblock.name)
                            fw('_points[')
                            fw('%d]' % vertex.index)
                            fw('[%d]-' % com_index)
                            fw('%s' % mesh.name)
                            fw('_')
                            fw('%s' % keyblock.relative_key.name)
                            fw('_points[')
                            fw('%d]' % vertex.index)
                            fw('[%d])*' % com_index)
                            fw('%s' % keyblock.name)
                            fw('_value/100)')
                fw(']')
            fw('];')
                            
            
#           fw('polyhedron(\n')
#           fw('triangles=[')
#           for f, f_index in face_index_pairs:
#               f_v_orig = [(vi, me_verts[v_idx]) for vi, v_idx in enumerate(f.vertices)]
#       
#               # openscad has flipped winding and doesn't handle quads
#               if len(f_v_orig) == 3:
#                   f_v_iter = (f_v_orig[2], f_v_orig[1], f_v_orig[0]),
#               else:
#                   f_v_iter = (f_v_orig[2], f_v_orig[1], f_v_orig[0]), (f_v_orig[3], f_v_orig[2], f_v_orig[0])
#       
#               # support for triangulation
#               for f_v in f_v_iter:
#                   if len(globalVerts) != 0:
#                       fw(', ')
#                   fw('[')
#                   vertexIndex = 0
#                   for vi, v in f_v:
#                       if vertexIndex != 0:
#                           fw(',')
#                       vertexIndex += 1
#                       vertKey = veckey3d(v.co)
#                       if vertKey not in vertDict:
#                           vertIndex += 1
#                           globalVerts[vertIndex] = vertKey
#                           vertDict[vertKey] = vertIndex
#                           fw('%d' % vertIndex)
#                       else:
#                           fw('%d' % vertDict[vertKey])
#       
#                   face_vert_index += len(f_v)
#                   fw(']')
#           fw('],\n')
#           fw('points = [')
#           for vertKey, vi in enumerate(globalVerts):
#             if vi != 0:
#               fw(',')
#             fw('[%f,%f,%f]' % globalVerts[vi])
#           fw(']\n')
#           fw(');\n')

    file.close()

    # copy all collected files.
    bpy_extras.io_utils.path_reference_copy(copy_set)

    print("OpenSCAD Export time: %.2f" % (time.time() - time1))

def write_file( filepath, objects, scene,
                EXPORT_APPLY_MODIFIERS=True,
                EXPORT_PATH_MODE='AUTO',
                ):
    """
    Basic write function. The context and options must be already set
    """

    def veckey3d(v):
        return round(v.x, 6), round(v.y, 6), round(v.z, 6)

    time1 = time.time()

    file = open(filepath, "w", encoding="utf8", newline="\n")
    fw = file.write

    # Initialize totals, these are updated each object
    totverts = totuvco = totno = 1
    vertIndex = -1

    face_vert_index = 1

    globalVerts = {}
    vertDict = {}

    copy_set = set()

    # Get all meshes
    for ob_main in objects:

        # ignore dupli children
        if ob_main.parent and ob_main.parent.dupli_type in {'VERTS', 'FACES'}:
            continue

        obs = []
        if ob_main.dupli_type != 'NONE':
            ob_main.dupli_list_create(scene)
            obs = [(dob.object, dob.matrix) for dob in ob_main.dupli_list]
        else:
            obs = [(ob_main, ob_main.matrix_world)]

        for ob, ob_mat in obs:
            try:
                me = ob.to_mesh(scene, EXPORT_APPLY_MODIFIERS, 'PREVIEW')
            except RuntimeError:
                me = None
            if me is None:
                continue

            me_verts = me.vertices[:]

            # Make our own list so it can be sorted to reduce context switching
            face_index_pairs = [(face, index) for index, face in enumerate(me.tessfaces)]
            edges = []

            if not (len(face_index_pairs) + len(edges) + len(me.vertices)):  # Make sure there is somthing to write
                # clean up
                bpy.data.meshes.remove(me)
                continue  # dont bother with this mesh.

            fw('polyhedron(\n')
            fw('triangles=[')
            for f, f_index in face_index_pairs:
                f_v_orig = [(vi, me_verts[v_idx]) for vi, v_idx in enumerate(f.vertices)]

                # openscad has flipped winding and doesn't handle quads
                if len(f_v_orig) == 3:
                    f_v_iter = (f_v_orig[2], f_v_orig[1], f_v_orig[0]),
                else:
                    f_v_iter = (f_v_orig[2], f_v_orig[1], f_v_orig[0]), (f_v_orig[3], f_v_orig[2], f_v_orig[0])

                # support for triangulation
                for f_v in f_v_iter:
                    if len(globalVerts) != 0:
                        fw(', ')
                    fw('[')
                    vertexIndex = 0
                    for vi, v in f_v:
                        if vertexIndex != 0:
                            fw(',')
                        vertexIndex += 1
                        vertKey = veckey3d(v.co)
                        if vertKey not in vertDict:
                            vertIndex += 1
                            globalVerts[vertIndex] = vertKey
                            vertDict[vertKey] = vertIndex
                            fw('%d' % vertIndex)
                        else:
                            fw('%d' % vertDict[vertKey])

                    face_vert_index += len(f_v)
                    fw(']')
            fw('],\n')
            fw('points = [')
            for vertKey, vi in enumerate(globalVerts):
              if vi != 0:
                fw(',')
              fw('[%f,%f,%f]' % globalVerts[vi])
            fw(']\n')
            fw(');\n')

            # Make the indices global rather then per mesh
            totverts += len(me_verts)

            # clean up
            bpy.data.meshes.remove(me)

        if ob_main.dupli_type != 'NONE':
            ob_main.dupli_list_clear()

    file.close()

    # copy all collected files.
    bpy_extras.io_utils.path_reference_copy(copy_set)

    print("OpenSCAD Export time: %.2f" % (time.time() - time1))


def _write(context, filepath,
              EXPORT_APPLY_MODIFIERS,  # ok
              ):  # Not used

    print("saving to file: %s" % filepath)

    scene = context.scene
    # Exit edit mode before exporting, so current object states are exported properly.
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode='OBJECT')

    frame = scene.frame_current
    object = context.active_object
    objects = context.selected_objects

    # EXPORT THE SHAPES.
    write_shapes_file(filepath, object, scene,
               EXPORT_APPLY_MODIFIERS,
               )
               
# EXPORT THE FILE.
#     write_file(filepath, objects, scene,
#                EXPORT_APPLY_MODIFIERS,
#                )

def save(operator, context, filepath="",
         apply_modifiers=True
         ):

    _write(context, filepath,
           EXPORT_APPLY_MODIFIERS=apply_modifiers,
           )

    return {'FINISHED'}
