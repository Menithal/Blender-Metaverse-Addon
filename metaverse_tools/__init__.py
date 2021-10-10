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
# Copyright 2020 Matti 'Menithal' Lahtinen

bl_info = {
    "name": "Metaverse Toolkit Blender Add-on",
    "author": "Matti 'Menithal' Lahtinen",
    "version": (3, 0, 0),
    "blender": (2, 83, 0),
    "location": "File > Import-Export, Materials, Armature",
    "description": "Blender tools to allow for easier Content creation various platforms",
    "warning": "",
    "wiki_url": "",
    "support": "COMMUNITY",
    "category": "Import-Export",
}

import addon_utils
import sys
import logging
import bpy

from bpy.types import Operator, AddonPreferences
from bpy.props import StringProperty, IntProperty, BoolProperty

from metaverse_tools.ext.apply_modifier_for_object_with_shapekeys.ApplyModifierForObjectWithShapeKeys import ApplyModifierForObjectWithShapeKeysOperator

from metaverse_tools.utils.bones.custom import bones_binder_register, bones_binder_unregister, bones_scene_define, bones_scene_clean

from . import ui
from . import armature
from . import files
from . import utils


from .files.facerig import EXPORT_OT_MVT_TOOLSET_Writer_Facerig_Bundle_DAE
from .ext.modified_fbx_tools import EXPORT_OT_MVT_TOOLSET_FBX

from .utils.bpyutil import operator_exists
from .files.hifi_json.operator import *
from .files.fst.operator import *

from metaverse_tools.ext.apply_modifier_for_object_with_shapekeys.ApplyModifierForObjectWithShapeKeys import ApplyModifierForObjectWithShapeKeysOperator

def on_color_space_automation_update(self, context):
    print("Color Space Toggle", self.colorspaces_on_save, context)
    user_preferences = context.preferences
    addon_prefs = user_preferences.addons[__name__].preferences
    addon_prefs["automatic_color_space_fix"] = self.colorspaces_on_save


class MVTAddOnPreferences(AddonPreferences):
    bl_idname = __name__

    colorspaces_on_save: BoolProperty(name="Correct Color Space on save",
                                                     description="Correct Texture Color spaces for materials prior to saving.",
                                                    default=True,
                                                    update=on_color_space_automation_update)

    message_box: StringProperty(
        name="Status", default="", options={"SKIP_SAVE"})

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "colorspaces_on_save")


if "add_mesh_extra_objects" not in addon_utils.addons_fake_modules:
    print(" Could not find add_mesh_extra_objects, Trying to add it automatically. Otherwise install it first via Blender Add Ons")
    addon_utils.enable("add_mesh_extra_objects")


def reload_module(name):
    if name in sys.modules:
        del sys.modules[name]


def menu_func_import(self, context):
    self.layout.operator(IMPORT_OT_MVT_TOOLSET_Scene_From_JSON.bl_idname,
                         text="HiFi Metaverse Scene JSON (.json)")


def menu_func_export(self, context):
    
    self.layout.operator(EXPORT_OT_MVT_TOOLSET_FBX.bl_idname, text="Vircadia FBX (.fbx)")
    self.layout.operator(EXPORT_OT_MVT_TOOLSET_Hifi_FST_Writer_Operator.bl_idname,
                         text="Vircadia Avatar FST (.fst)")
   # self.layout.operator(EXPORT_OT_MVT_TOOLSET_Writer_GLTF_JSON.bl_idname,
   #                      text="HiFi Metaverse Scene JSON / GLTF (.json/.glb/.glm)")
    self.layout.operator(EXPORT_OT_MVT_TOOLSET_Writer_FBX_JSON.bl_idname,
                         text="Vircadia Metaverse Scene JSON / FBX (.json/.fbx)")
    self.layout.operator(EXPORT_OT_MVT_TOOLSET_Writer_Facerig_Bundle_DAE.bl_idname,
                         text="FaceRig/Animaze Bundle Export (.dae)")


classes = (
    EXPORT_OT_MVT_TOOLSET_Message_Error_Missing_ATP_Override,
    EXPORT_OT_MVT_TOOLSET_Writer_GLTF_JSON,
    EXPORT_OT_MVT_TOOLSET_Writer_FBX_JSON,
    EXPORT_OT_MVT_TOOLSET_Writer_Facerig_Bundle_DAE,
    EXPORT_OT_MVT_TOOLSET_FBX,
    IMPORT_OT_MVT_TOOLSET_Scene_From_JSON,
    MVTAddOnPreferences,
)

main_register, main_unregister = bpy.utils.register_classes_factory(classes)    


existing_shapekey_merger = False
bpy.app.handlers.save_pre.append(utils.helpers.materials.correct_all_color_spaces_to_non_color)

def register():
    main_register()
    bones_binder_register()
    bones_scene_define()

    existing_shapekey_merger = operator_exists(ApplyModifierForObjectWithShapeKeysOperator.bl_idname)
    if  existing_shapekey_merger == False:
        print ("Registering bundled ApplyModifierForObjectWithShapeKeysOperator")
        bpy.utils.register_class(ApplyModifierForObjectWithShapeKeysOperator)
    else: 
        print ("Existing ApplyModifierForObjectWithShapeKeysOperator found")
        existing_shapekey_merger = True

    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)
    ui.register_operators()



def unregister():
    main_unregister()
    bones_binder_unregister()
    bones_scene_clean()

    if  existing_shapekey_merger == False:
        bpy.utils.unregister_class(ApplyModifierForObjectWithShapeKeysOperator)

    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    ui.unregister_operators()
