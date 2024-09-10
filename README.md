# Blender Metaverse Toolkit Blender Add-on (MVT) AddOn

Plugin ("Project Hermes") is a plugin for Blender to allow for easier content creation originally created for importing for the High Fidelity Metaverse Platform. 

It has now being expanded to support additional platforms. as the official High Fidelity platform is turning off, while its forks are going to live their separate lives.
This plugin now will focus on supporting as many platforms as possible.

Currently Supports

- HiFi and Forks
- VRC (NeosVR by Proxy)
- Tower Unite
- Faceshift/Animaze

## 3.1+ Works with blender 2.90 or later.

# Installation Guide

## Simple
Open the Github page, Go to releases and download the `metaverse_tools.zip` zip file. 

In Blender. Goto `User Preferences`, and `Add-ons`. From there `Install Add-on from File` and select the Zip file that we downloaded.

Enable the plugin under `Import-Export: Metaverse Toolkit Blender Add-on`.

### If you had previous used plugin when it was "High Fidelity" Only, make sure to uninstall the old one first.

## If you use the git repository:

Make sure to `git submodule init` and `git submodule update` as we are using an external add on to bind shapkeys to new model.

Copy `metaverse_tools` folder to your Blender Addons Directory. 

On Windows this is under `%APPDATA%/Blender Foundation/Blender/<BlenderVersion>/addons`


# Utility Functions:

### General Tools

- Mesh Tools:
    - `Merge Modifiers & Shapekeys` attempt to merge modifiers onto Mesh with Shapekeys using Przemysław Bągard's ApplyModifierForObjectWithShapeKeys script, now included with this plugin, but if an existing copy exists, it is used instead
    - `Clean Unused Vertex Groups` Clean model from vertex groups that are not in its current skeleton.
- Armature Tools:
    - `Test Avatar Rest Pose` - Attempts to detect type of skeleton and applies an absolute T-Pose by the platform reference
    - `Merge Bones` - Attempts to merge selected bones to last selected bone.
    - `Match Reference Rolls` - Uses rolls from the detected reference skeleton.

### VRChat / Resonite Tools (WIP) 

Work in progress module to try to stream line some "gotchas" when converting avatars to VRC without the duplicate operator additions from CATS (creating operators for Tools that are already in Blender, which create abit of clutter during operator searches). Also by proxy supports NeosVR, which automatically binds the visemes when fbx export is used.

- A new Panel on the `3D View`'s right tool set is added, labled `MVT: VRC Tools`
- Armature Tools
    - `Add VRC Armature` - Adds an Armature which is compatible with VRC
    - `Generate VRC Shapekeys` - Generates empty shapekeys (for now, later will allow the use of various methods, including CATS, and custom)
    - `Sort Shapekeys` - Utility function to quickly sort shapekeys to match VRC requirements.

### Tower Unite Tools (WIP)

Work in progress module to try to stream line some "gotchas" when converting avatars to TE.

- A new Panel on the `3D View`'s right tool set is added, labled `MVT: TowerUnite Tools`
- Armature Tools
    - `Add TU Armature` - Adds an Armature which is compatible with Tower Unite
    - `Clean Shapekeys` - Utility function to quickly remove all shapekeys from a model
    - `Fix Common Issues` - Utility function to remove all weights for  root, and all the twist bones that tend to cause issues.


### Generic Rigging tools:

Mostly Tools for assisting with creating rigs for animations into various platforms and engines.

- `Pose Contraint tools`:
    - `Clear Constraint` - Allows fast clearing of constraints
    - `Location Copy` - Sets up Pose Location Constraint for selected bones to copy the root
    - `Influenced Copy` - Sets up a Pose Location constraint for selected bones with influence based on distance to active
    - `Rotational Copy` - Sets up a Pose Rotation constraints for selected bones to copy the root
    - `Mirror Constraint` - Copies all  Constraints from other bones, and mirrors it to the other side.
    - `Normalize Constraints` - Normalizes influences for a bone with multiple constraints of the same type.

- `Pose Utility Tools`:
    - `Clone Locks` - Clones position and rotation locks from one bone to the other
    - `Un/Lock Rotations` - Locks all rotations for bone
    - `Un/lock Translations` - Unlocks all Translations
    - `Copy Custom Shapes` - Copies custom bone shapes from one to selected.
    - `Clear Custom Shapes` - Clears all custom bone shapes.


# Changelog:

### 3.1.0
- Added `Facerig/Animaze Bundle export` - Creates a folder structure taht is compatible with animaze/facerig
- Hifi->Vircadia rename
- `Split Mirrorable Actions` Mirror Actions into Actions allowing creation of mirrored actions
- Using latest Apply Modifiers version for better Blender 2.90+ compatability

### 2.1.0
- Added Hotfix #29 and #28 Relating to Hifi FBX and the FBX changes in 2.8
- Added `Pose Constraint Tools` for dealing with bone constraints
- Added `Pose Utility Tools` for dealing with bone behavior

### 2.0.1
- Added some sculpting tools to quickly add 0.05 and reduce 0.05 resolution prior to remesh
- Moved compartmentalized components around for more easier maintenance in the future.
- README improvements

### 2.0
- `hifi_tools` is now `metaverse_tools`
- Added Tower Unite specific tools
- Fixed 2.81 FBX export (but may have forgotten 2.8)

### 1.5.5

- Hifi_tools is in the process of renaming to mvt_tools, in version 2.0 this will occur
- Added VRChat Specific tools (WIP) for experienced blenderers.
- Prepared framework for ability to import and on-the-fly create multiple platform skeletons and retarget animations cross-platform.
- Fixed issues with Hifi FBX export, regarding emissions


### 1.4x

- 2.8 RC support
- Removed eBPBRS infavor of just using the PBR Materials.
- Lots of Refactoring