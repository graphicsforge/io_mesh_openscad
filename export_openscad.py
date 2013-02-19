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

def getName( object ):
  return re.sub( '[\. ]','_', object.data.name )

# dump some stuff we might want later in openscad
def write_utils( fw, object ):
  objectName = getName(object)
  fw("function %s_dimX() = %.2f;\n" % (objectName, object.dimensions[0]))
  fw("function %s_dimY() = %.2f;\n" % (objectName, object.dimensions[1]))
  fw("function %s_dimZ() = %.2f;\n" % (objectName, object.dimensions[2]))

# output our comments about shapekey objects
def write_shapekey_commments( fw, object ):
  objectName = getName(object)
  mesh = object.data
  if (len(mesh.polygons) + len(mesh.vertices)):
    # grab our shapekeys, excluding our reference
    nonRefShapeKeys = {}
    for index, keyblock in enumerate(mesh.shape_keys.key_blocks):
      if keyblock.name == mesh.shape_keys.reference_key.name:
        continue
      else:
        nonRefShapeKeys[len(nonRefShapeKeys)] = keyblock

    # drop our info
    fw("\n/////////////////////\n")
    fw("// MODULE %s\n" % objectName)
    fw("/////////////////////\n")
    fw("// Control Variables\n")
    for i, key in enumerate(nonRefShapeKeys):
      fw("%s_factor = %d; // [%d, %d]\n" % (nonRefShapeKeys[i].name, nonRefShapeKeys[i].value*100, nonRefShapeKeys[i].slider_min*100, nonRefShapeKeys[i].slider_max*100))
    fw("\n// Examples/Tests\n")
    fw("%s(" % objectName)
    for i, key in enumerate(nonRefShapeKeys):
      if i!=0:
        fw(", ")
      fw("%s_factor" % nonRefShapeKeys[i].name)
    fw(");\n")
    fw("\n// Functions and Utilities\n")
    write_utils( fw, object )

# output our comments about objects
def write_object_commments( fw, object ):
  objectName = getName(object)
  mesh = object.data
  if (len(mesh.polygons) + len(mesh.vertices)):
    # drop our info
    fw("\n/////////////////////\n")
    fw("// MODULE %s\n" % objectName)
    fw("/////////////////////\n")
    fw("\n// Examples/Tests\n")
    fw("%s();\n" % objectName)
    fw("\n// Functions and Utilities\n")
    write_utils( fw, object )

# output an object that has shapekeys
def write_shapekeys( fw, object, EXPORT_CUSTOMIZER_MARKUP=False ):
  objectName = getName(object)

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
    fw("\n/////////////////////\n// geometry for %s\n" % objectName)
    fw("function %s_triangles() = [\n" % objectName)
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
        fw("function %s_%s_points() = [\n" % (objectName, keyblock.name))
        for index, vertex in enumerate(keyblock.data):
            if index != 0:
                fw(",")
            fw("[%f,%f,%f]" % (vertex.co.x,vertex.co.y,vertex.co.z))
        fw("];\n")

    fw("module %s(" % objectName)
    for i, key in enumerate(nonRefShapeKeys):
      if i!=0:
        fw(", ")
      fw("%s_factor = %f" % (nonRefShapeKeys[i].name, nonRefShapeKeys[i].value*100))
    fw(") {\n")

    fw("  %s_shapes_points = [\n" % objectName)
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
            fw("%f" % (keyblock.data[vertex.index].co[com_index]))
          else:
            # linearly interpolate between key and base
            fw("((%f-%f)" % (keyblock.data[vertex.index].co[com_index], keyblock.relative_key.data[vertex.index].co[com_index]))
            fw("*%s_factor/100)" % keyblock.name)
      fw("]")
    fw("];")
    fw("  polyhedron(triangles = %s_triangles(), points = %s_shapes_points);\n" % (objectName, objectName))
    fw("};\n")

  else:
    print("ERROR: tried to export a mesh without sufficient verts!")

# output an object
def write_object( fw, object, mesh ):
  objectName = getName(object)

  # if an object has geometry, export them
  if (len(mesh.polygons) + len(mesh.vertices)):
    # drop our geometry
    fw("\n/////////////////////\n// geometry for %s\n" % objectName)
    fw("function %s_triangles() = [\n" % objectName)
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
    fw("function %s_points() = [\n" % objectName)
    for vertex in mesh.vertices:
      if vertex.index != 0:
        fw(",")
      fw("[%f,%f,%f]" % (vertex.co.x,vertex.co.y,vertex.co.z))
    fw("];")
    # define our module
    fw("module %s() {\n" % objectName)
    fw("  polyhedron(triangles = %s_triangles(), points = %s_points());\n" % (objectName, objectName))
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
