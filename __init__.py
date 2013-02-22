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

# <pep8-80 compliant>

bl_info = {
    "name": "OpenSCAD Exporter (.scad)",
    "author": "Peter Yee (GraphicsForge)",
    "version": (0, 2),
    "blender": (2, 6, 6),
    "location": "File > Import-Export > openscad",
    "description": "Output a mesh into an openscad file",
    "warning": "",
    "wiki_url": "https://github.com/graphicsforge/io_mesh_openscad/wiki",
    "tracker_url": "https://github.com/graphicsforge/io_mesh_openscad",
    "support": 'COMMUNITY',
    "category": "Import-Export"}

"""
Export OpenSCAD files
"""

if "bpy" in locals():
  import imp
  if "export_openscad" in locals():
    imp.reload(export_openscad)

import os
import bpy
from bpy.props import StringProperty, BoolProperty, CollectionProperty
from bpy_extras.io_utils import ExportHelper, ImportHelper
from bpy.types import Operator, OperatorFileListElement


class ExportOpenSCAD(Operator, ExportHelper):
  """Save vertex array data from the active object"""
  bl_idname = "export_mesh.openscad"
  bl_label = "Export OpenSCAD"

  filename_ext = ".scad"
  filter_glob = StringProperty(default="*.scad", options={'HIDDEN'})

  apply_modifiers = BoolProperty(name="Apply Modifiers",
                   description="Apply the modifiers first",
                   default=True)

  def execute(self, context):
    from . import export_openscad
    from mathutils import Matrix

    keywords = self.as_keywords(ignore=("check_existing",
                                        "filter_glob",
                                        ))

    return export_openscad.save(self, context, **keywords)


def menu_export(self, context):
  default_path = os.path.splitext(bpy.data.filepath)[0] + ".scad"
  self.layout.operator(ExportOpenSCAD.bl_idname, text="openscad (.scad)")


def register():
  bpy.utils.register_module(__name__)
  bpy.types.INFO_MT_file_export.append(menu_export)


def unregister():
  bpy.utils.unregister_module(__name__)
  bpy.types.INFO_MT_file_export.remove(menu_export)


if __name__ == "__main__":
  register()
