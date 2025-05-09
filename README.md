# How To Install
1. Save the code and copy it into your maya scripts directory. For example: C:/Users/<YourUsername>/Documents/maya/scripts/
2. In mayas script editor use these two lines of code to run:
   import auto_skin_plugin
   auto_skin_plugin.launch_auto_skin_plugin()
--------

## Auto Skin-Weighter

Automatically binds and weights meshes to joints

* Creates new skin cluster and deletes the old
* Binds skin to joints
* Applies smooth and simplified weighting
   (ideal weighting still needs to be done by hand)
* allows for the selection of multiple meshes
* mirrors weighting
* Allows user to manual set max number of joints influenced per vertex
