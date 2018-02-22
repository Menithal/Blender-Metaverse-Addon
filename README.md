# Blender Hifi AddOn

This add On project ("Hermes") is a community driven project started by Menithal to 
create a plugin for blender to allow for easier content creation for the High Fidelity Metaverse.


# Installation Guide

Open the Github page, and press `Clone or download` and download as zip.

In Blender. Goto `User Preferences`, and `Add-ons`. From there `Install Add-on from File` and select the Zip file that we downloaded.

Enable the plugin under `Import-Export: Hifi Blender Add-On`



# Use

For now, the add-on allows you to import primitive entities from High Fidelity. Simple select the entities you want to export and press export. 

In Blender, You can then import these entities with `File > Import > High Fidelity JSON`


# Settings

- Use UV Sphere: Instead of a Quad sphere, use a UV sphere for the base primitive
- Join Mesh Children: If Boolean is set to None, join Children with their Parents into a Single Mesh
- Merge Distance: Set this higher if you want to remove doubles
- Delete interior faces: If the mesh is enclosed and not consisting of multiple convex intercepting shapes, delete interior walls 
- Boolean: Experimental feature to enable
    - None: Use no boolean solver to solve for faces
    - BMesh: Experimental: Use BMesh solver to solve for mesh
    - Carve: Experimental Use Carge solver to solve for mesh

If Entity is not Child of another entity, no Join is done. Only Children are merged with their Parents

Note that Boolean operations work differently, and some may not keep the UV Unwrapping correctly in some situations. Use at your own risk