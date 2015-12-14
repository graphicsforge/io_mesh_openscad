io_mesh_openscad
================

Blender output module for OpenSCAD

A module for blender 2.74 that outputs meshes in OpenSCAD compatible format.
Clone into your blender addon directory, and enable in your user preferences.

OpenSCAD is http://www.openscad.org/

Version History
================
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
