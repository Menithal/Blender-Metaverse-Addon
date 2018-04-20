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


bl_info = {
    "name": "HiFi Blender Add-on",
    "author": "Matti 'Menithal' Lahtinen",
    "version": (0,8,4),
    "blender": (2,7,7),
    "location": "File > Import-Export, Materials, Armature",
    "description": "Blender tools to allow for easier Content creation for High Fidelity",
    "warning": "",
    "wiki_url": "",
    "support": "COMMUNITY",
    "category": "Import-Export",
}


import addon_utils
import sys
import logging

if "bpy" in locals():
    if bpy.app.version < (2, 71, 0):
        import imp as importlib
    else:
        import importlib
    
    importlib.reload(utils)
    importlib.reload(world)
    importlib.reload(armature)
    importlib.reload(files)

else:
    print("Load World")
    from . import utils
    from . import world
    from . import armature

    from .files.hifi_json.operator import *
    
    import bpy


if "add_mesh_extra_objects" not in addon_utils.addons_fake_modules:
    print(" Could not find add_mesh_extra_objects, Trying to add it automatically. Otherwise install it first via Blender Add Ons")
    addon_utils.enable("add_mesh_extra_objects")

def reload_module(name): 
    if name in sys.modules: 
        del sys.modules[name]

def menu_func_import(self, context):
    self.layout.operator(JSONLoaderOperator.bl_idname, text="HiFi Metaverse Scene JSON (.json)")
   
def menu_func_export(self,context):
    self.layout.operator(JSONWriterOperator.bl_idname, text="HiFi Metaverse Scene JSON / FBX (.json/.fbx)")

def register():
    bpy.utils.register_module(__name__) #Magic Function!
    bpy.types.INFO_MT_file_import.append(menu_func_import)
    bpy.types.INFO_MT_file_export.append(menu_func_export)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)
 
if __name__ == "__main__":
    register()
