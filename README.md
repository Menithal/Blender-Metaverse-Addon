# Blender Metaverse Toolset (MVT) AddOn

Plugin ("Project Hermes") is a plugin for Blender to allow for easier content creation originally created for importing for the High Fidelity Metaverse Platform. 

It has now being expanded to support additional platforms.

## 1.5+ works only with Blender 2.80 RC+

# Installation Guide

## Simple
Open the Github page, Go to releases and download the `hifi_tools.zip` zip file.

In Blender. Goto `User Preferences`, and `Add-ons`. From there `Install Add-on from File` and select the Zip file that we downloaded.

Enable the plugin under `Import-Export: MVT Blender Add-On`.

### If you had previous used plugin when it was "High Fidelity" Only, make sure to uninstall the old one first.


## If you downloaded the download repository:

Copy `hifi_tools` folder to your Blender Addons Directory. 

On Windows this is under `%APPDATA%/Blender Foundation/Blender/<BlenderVersion>/addons`

# Changes:

- Hifi_tools is in the process of renaming to mvt_tools, in version 2.0 this will occur
- Added VRChat Specific tools (WIP) for experienced blenderers.
- Prepared framework for ability to import and on-the-fly create multiple platform skeletons and retarget animations cross-platform.
- Fixed issues with Hifi FBX export, regarding emissions


# Utility Functions:

### General Tools

- Material Tools
   - Automatic `Principled BDSF` binding to HF FBX. You can use Blender materials to define HF materials, just do not use Node Groups.
   - `Set Non-Diffuse ColorData` and `Auto Correct on Save` Tools that fixes color spaces for Roughness, Normal, and Metallic textures for preview
   - `Textures to Mask` and `Textures to Png` utility helpers.
- Mesh Tools:
    - `Merge Modifiers & Shapekeys` attempt to merge modifiers onto Mesh with Shapekeys using Przemysław Bągard's ApplyModifierForObjectWithShapeKeys script, now included with this plugin, but if an existing copy exists, it is used instead
    - `Clean Unused Vertex Groups` Clean model from vertex groups that are no in its skeleton.
- Armature Tools:
    - `Test Avatar Rest Pose` - Attempts to detect type of skeleton and applies an absolute T-Pose by the platform reference
    - `Merge Bones` - Attempts to merge selected bones to last selected bone.
    - `Match Reference Rolls` - Uses rolls from the detected reference skeleton.



### High Fidelity Tools

Generic Toolset allowing one to create content for High Fidelity, from 

- A new Panel on the `3D View`'s right tool set is added, labled `MVT: High Fidelity`
- Armature Tools
    - `Add Hifi Armature` - Adds an Armature which is compatible with High Fidelity, has all the naming conventions in place
    - `Set Bone Physical` - (Armature Edit mode only) Adds a prefix to selected bones for Scripts in High fidelity for physical simulation
    - `Remove Bone Physical` - (Armature Edit mode only) Removes prefix from selected bones for Scripts in High fidelity for physical simulation
- Avatar Converters
    - `Custom Avatar` - Attempts to bind of the model to a HF specific Bone naming and rotations.
    - `MMD Avatar` - Translates and fixes MMD models and their materials for them to work in High Fidelity. [Full MMD Avatar import tutorial here](https://www.youtube.com/watch?v=tJX8VUPZLKQ)


#### Hifi Export Tools:

- `File > Export > Hifi FBX`: Custom FBX that binds to the `Principled BDSF` into a format HiFi understands
- `File > Export > Hifi Avatar FST`: Exports Avatar, applies necessary steps for avatar to work in High Fifelity. 
   - Supports Embedded textures: Exports Textures embedded to file
   - Supports Selected Only: Exports Selected only
   - Experimental Oven Feature:  Experimental feature to Compress Avatar and its Textures: Only settable if you have set the path under `User Settings > Addon > HiFi Blender Add-on`
- `File > Export > HiFi Metaverse Scene JSON/FBX`: Exports Scene as a json and Fbx
    - Marketplace / Base URL : This is the folder path for your marketplace or external server address. Simply paste the directory where you will upload the files here, and the json file will have the urls automatically appended to them. This is not optional and must be set prior to exporting: You will otherwise have an error message
    - Clone Scene prior to export

#### Importing from Hifi:
The add-on allows you to import **primitive entities**  from High Fidelity. In High Fidelity,  select the entities you want to export and press export. 

In Blender, You can then import these entities with `File > Import > HiFi Metaverse Scene JSON`

You can then set materials to the objects via the material panel, modify the mesh, do uv mapping corrections.

#### Hifi Import Settings

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



### VRChat Tools (WIP) 

Work in progress module to try to stream line some "gotchas" when converting avatars to VRC without the duplicate operator additions from CATS (creating operators for Tools that are already in Blender, which create abit of clutter during operator searches)

- A new Panel on the `3D View`'s right tool set is added, labled `MVT: VRC Tools`
- Armature Tools
    - `Add VRC Armature` - Adds an Armature which is compatible with VRC
    - `Generate VRC Shapekeys` - Generates empty shapekeys (for now, later will allow the use of various methods, including CATS, and custom)
    - `Sort Shapekeys` - Utility function to quickly sort shapekeys to match VRC requirements.

