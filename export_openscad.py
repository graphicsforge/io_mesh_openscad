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
import re
import time

import bpy
import mathutils
import bpy_extras.io_utils

# dump some stuff we might want later in openscad
def write_info( fw, object ):
  fw("// set info variables for %s\n" % object.data.name)
  fw("%s_dims = [%.2f,%.2f,%.2f];\n" % (object.data.name,object.dimensions[0],object.dimensions[1],object.dimensions[2]))
  fw("%s_num_verts = %d;\n" % (object.data.name,len(object.data.vertices)))

# output our comments about shapekey objects
def write_shapekey_commments( fw, object ):
  mesh = object.data
  if (len(mesh.polygons) + len(mesh.vertices)):
    # grab our shapekeys, excluding our reference
    nonRefShapeKeys = {}
    for index, keyblock in enumerate(mesh.shape_keys.key_blocks):
      if keyblock.name == mesh.shape_keys.reference_key.name:
        continue
      else:
        nonRefShapeKeys[len(nonRefShapeKeys)] = keyblock

    # say what we're going to do
    fw("\n//exports module %s(" % mesh.name)
    for i, key in enumerate(nonRefShapeKeys):
      if i!=0:
        fw(",\n//\t\t\t")
      fw("%s_value = 0" % nonRefShapeKeys[i].name)
    fw(")\n")

    # draw the mesh with default key values
    fw("//draw geometry like this\n%s();\n" % mesh.name)

    # drop info variables
    write_info( fw, object )

# output our comments about objects
def write_object_commments( fw, object ):
  mesh = object.data
  if (len(mesh.polygons) + len(mesh.vertices)):
    # say what we're going to do
    fw("\n//exports module %s()\n" % mesh.name)

    # draw the mesh with default key values
    fw("//draw geometry like this\n%s();\n" % mesh.name)

    # drop info variables
    write_info( fw, object )

# output an object that has shapekeys
def write_shapekeys( fw, object, EXPORT_CUSTOMIZER_MARKUP=False ):

  # if an object has geometry, export them
  mesh = object.data
  if (len(mesh.polygons) + len(mesh.vertices)):
    # grab our shapekeys, excluding our reference
    nonRefShapeKeys = {}
    for index, keyblock in enumerate(mesh.shape_keys.key_blocks):
      if keyblock.name == mesh.shape_keys.reference_key.name:
        continue
      else:
        nonRefShapeKeys[len(nonRefShapeKeys)] = keyblock

    # drop our geometry
    fw("\n\n// this is the geometry for %s (sorry, not human editable)\n" % mesh.name)
    fw("%s_triangles = [\n" % mesh.name)
    for index, face in enumerate(mesh.polygons):
      face_verts = face.vertices
      if index != 0:
          fw(',')
      # fan triangulate
      for i in range(2, len(face_verts), 1):
        if i>2:
          fw(",")
        fw("[%d,%d,%d]" % (face_verts[i],face_verts[i-1],face_verts[0]))
    fw("];\n")
    
    for index, keyblock in enumerate(mesh.shape_keys.key_blocks):
        shape_verts_index = [(index, shape_vertex) for index, shape_vertex in enumerate(keyblock.data)]
        fw("%s_%s_points=[\n" % (mesh.name, keyblock.name))
        for index, vertex in shape_verts_index:
            if index != 0:
                fw(",")
            fw("[%f,%f,%f]" % (vertex.co.x,vertex.co.y,vertex.co.z))
        fw("];\n")

    fw("module %s(" % mesh.name)
    for i, key in enumerate(nonRefShapeKeys):
      if i!=0:
        fw(", ")
      fw("%s_value = 0" % nonRefShapeKeys[i].name)
    fw(") {\n")

    fw("  %s_shapes_points = [\n" % mesh.name)
    for vertex in mesh.vertices:
      if vertex.index != 0:
        fw(",")
      fw("[")
      for com_index, component in enumerate(vertex.co):
        if com_index != 0:
          fw(",")
        for key_index, keyblock in enumerate(mesh.shape_keys.key_blocks):
          # combine the effect of each shapekey
          if key_index != 0:
            fw("+")
          if keyblock.name == mesh.shape_keys.reference_key.name:
            fw("%s_%s_points[%d][%d]" % (mesh.name, keyblock.name, vertex.index, com_index))
          else:
            # linearly interpolate between key and base
            fw("((%s_%s_points[%d][%d]-" % (mesh.name, keyblock.name, vertex.index, com_index))
            fw("%s_%s_points[%d][%d])*" % (mesh.name, keyblock.relative_key.name, vertex.index, com_index))
            fw("%s_value/100)" % keyblock.name)
      fw("]")
    fw("];")
    fw("  polyhedron(triangles = %s_triangles, points = %s_shapes_points);\n" % (mesh.name, mesh.name))
    fw("};\n")

  else:
    print("ERROR: tried to export a mesh without sufficient verts!")

# output an object
def write_object( fw, object, mesh ):

  # if an object has geometry, export them
  if (len(mesh.polygons) + len(mesh.vertices)):
    # drop our geometry
    fw("\n\n// this is the geometry for %s (sorry, not human editable)\n" % object.data.name)
    fw("%s_triangles = [\n" % object.data.name)
    for index, face in enumerate(mesh.polygons):
      face_verts = face.vertices
      if index != 0:
          fw(',')
      # fan triangulate
      for i in range(2, len(face_verts), 1):
        if i>2:
          fw(",")
        fw("[%d,%d,%d]" % (face_verts[i],face_verts[i-1],face_verts[0]))
    fw("];\n")
    # drop our vert positions
    fw("%s_points = [\n" % object.data.name)
    for vertex in mesh.vertices:
      if vertex.index != 0:
        fw(",")
      fw("[%f,%f,%f]" % (vertex.co.x,vertex.co.y,vertex.co.z))
    fw("];")
    # define our module
    fw("module %s() {\n" % object.data.name)
    fw("  polyhedron(triangles = %s_triangles, points = %s_points);\n" % (object.data.name, object.data.name))
    fw("};\n")
  else:
    print("ERROR: tried to export a mesh without sufficient verts!")

def _write(context, filepath,
              EXPORT_APPLY_MODIFIERS,
              ):

  time1 = time.time() # profile how long we take
  print("saving to file: %s" % filepath)
  file = open(filepath, "w", encoding="utf8", newline="\n")
  filename_prefix=re.sub(
      '[\. ]','_'
      ,os.path.splitext( os.path.basename( file.name ) )[0]
      )
  fw = file.write
  fw("""//
//  Usage:
//
//    To reference this file in another OpenSCAD file
//      use <"""+filename_prefix+""".scad>;
""")

  scene = context.scene
  # Exit edit mode before exporting, so current object states are exported properly.
  if bpy.ops.object.mode_set.poll():
    bpy.ops.object.mode_set(mode='OBJECT')
  for object in context.selected_objects:
    if object.type == 'MESH' and object.data.shape_keys:
      write_shapekey_commments(fw, object)
    else:
      if object.type=='MESH':
        write_object_commments(fw, object)

  for object in context.selected_objects:

    # EXPORT THE SHAPES.
    if object.type == 'MESH' and object.data.shape_keys:
      write_shapekeys(fw, object,
               )
    else:
      if object.type=='MESH':
        write_object(fw, object, object.to_mesh(scene, EXPORT_APPLY_MODIFIERS, 'PREVIEW'),
               )

  # we're done here
  file.close()
  print("OpenSCAD Export time: %.2f" % (time.time() - time1))
 
def save(operator, context, filepath="",
         apply_modifiers=True,
         ):

  _write(context, filepath,
         EXPORT_APPLY_MODIFIERS=apply_modifiers,
         )

  return {'FINISHED'}
