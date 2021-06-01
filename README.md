io_mesh_openscad
================

Blender output module for [OpenSCAD](http://www.openscad.org/)

A module for Blender 2.8x that outputs meshes in [OpenSCAD](http://www.openscad.org/) compatible format.
Clone into your blender addon directory ([Blender's Directory Layout](https://docs.blender.org/manual/en/latest/advanced/blender_directory_layout.html)), and enable in your user preferences.

Version History
================
v0.4.1 
 - make addon compatible with blender version >= 2.8x

v0.4
 - support for multi spline paths ( [atartanian](https://github.com/atartanian) )

v0.3
 - exports curves as polygons instead of polyhedron
 - fixed multimatrix function after I borked it ( [clothbot](https://github.com/clothbot) )

v0.2
 - make output files modular for `use` in other openscad files ( [clothbot](https://github.com/clothbot) )
 - output shapekeys ( [atartanian](https://github.com/atartanian) )
 - handle n-gons
 - fix bug exporting multiple models

v0.1
 - initial version
