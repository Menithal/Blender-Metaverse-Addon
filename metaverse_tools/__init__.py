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
# Copyright 2019 Matti 'Menithal' Lahtinen

bl_info = {
    "name": "Metaverse Toolkit Blender Add-on",
    "author": "Matti 'Menithal' Lahtinen",
    "version": (2, 1, 0),
    "blender": (2, 81, 0),
    "location": "File > Import-Export, Materials, Armature",
    "description": "Blender tools to allow for easier Content creation various platforms",
    "warning": "",
    "wiki_url": "",
    "support": "COMMUNITY",
    "category": "Import-Export",
}

default_gateway_server = ""
oauth_api = "https://metaverse.highfidelity.com/user/tokens/new?for_identity=true"
oauth_default = True

import addon_utils
import sys
import logging
import webbrowser
import bpy


from bpy.types import AddonPreferences
from bpy.app.handlers import persistent

from metaverse_tools.ext.throttle import throttle
from metaverse_tools.ext.modified_fbx_tools import *
from metaverse_tools.utils.helpers.panel_context import toggle_console

from . import armature
from . import ui
from . import utils
from . import files
from .utils.bpyutil import operator_exists
from .files.hifi_json.operator import *
from .files.fst.operator import *
from .gateway import client as GatewayClient

from metaverse_tools.utils.bones.custom import custom_register, custom_unregister, scene_define, scene_delete
from metaverse_tools.ext.apply_modifier_for_object_with_shapekeys.ApplyModifierForObjectWithShapeKeys import ApplyModifierForObjectWithShapeKeysOperator

# TODO: This is placeholder and will be shut down after more are available.

def on_server_update(self, context):
    user_preferences = context.preferences
    addon_prefs = user_preferences.addons[__name__].preferences

    if len(addon_prefs["gateway_server"]) > 0 and len(addon_prefs["gateway_username"]) > 0:
        print("Server address updated" + addon_prefs["gateway_server"])
        result = GatewayClient.routes(addon_prefs["gateway_server"])

        if "oauth" in result:
            addon_prefs["oauth_required"] = result["oauth"]
            addon_prefs["oauth_api"] = result["oauth_api"]
        else:
            addon_prefs["oauth_required"] = False
            addon_prefs["oauth_api"] = ""

    else:
        addon_prefs["oauth_required"] = False
        addon_prefs["oauth_api"] = ""
        addon_prefs["gateway_username"] = ""
        addon_prefs["hifi_oauth"] = ""

    return None


def on_token_update(self, context):
    user_preferences = context.preferences
    addon_prefs = user_preferences.addons[__name__].preferences

    wm = context.window_manager
    username = addon_prefs["gateway_username"]

    if len(username) == 0:
        toggle_console()
            
        addon_prefs["gateway_token"] = ""
        addon_prefs["message_box"] = "No username set."
        return None

    if not "gateway_server" in addon_prefs.keys():
        addon_prefs["gateway_server"] = default_gateway_server

    server = addon_prefs["gateway_server"]

    if "oauth" in addon_prefs and addon_prefs["oauth"] or oauth_default:
        if addon_prefs["hifi_oauth"] is not None:
            response = GatewayClient.new_token_oauth(
                server, username, addon_prefs["hifi_oauth"])
        else:
            return None
    else:
        response = GatewayClient.new_token(server, username)

    result = response[0]
    message = response[1]
    if result is "Err":
        addon_prefs["gateway_token"] = ""
        addon_prefs["message_box"] = message
        return None

    addon_prefs["gateway_token"] = message
    addon_prefs["message_box"] = ""  # Success! Remember to Save Settings.
    bpy.ops.metaverse_toolset_messages.auth_success('INVOKE_DEFAULT')

    return None

def on_color_space_automation_update(self, context):
    print("Color Space Toggle", self.colorspaces_on_save, context)
    user_preferences = context.preferences
    addon_prefs = user_preferences.addons[__name__].preferences
    addon_prefs["automatic_color_space_fix"] = self.colorspaces_on_save


# Blender Naming convention is  bonkers. Operators must be bl_idname bmust specifically be <lower_case_plugin>.<lower_case_name> but naming Operators should be done using the NEW method. ARGH 
# While PANELS must be named using their NEW convention https://wiki.blender.org/wiki/Reference/Release_Notes/2.80/Python_API/Addons

# As far as I know this goes AGAINST Class naming scheme of python imo, where as Class names should follow the UpperCaseCamelCase convention...

class EXPORT_OT_MVT_TOOLSET_IPFS_Feature_Info (bpy.types.Operator):
    """ This Operator discuss about the IPFS Service
    """
    bl_idname = "metaverse_toolset.ipfs_feature_info"
    bl_label = "Enable IPFS"
    bl_options = {'REGISTER', 'INTERNAL'}

    agree: BoolProperty(
        name="Yes", description="I am aware what it means to upload to ipfs via the hifi-ipfs gateway.", default=False)

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.label(
            text="IPFS is Interplanetary File System, https://ipfs.io is a public, ", icon="INFO")

        row = layout.row()
        row.label(
            " distributed file network.")

        row = layout.row()
        row.label(
            "The Hifi-Blender plugin allows to use an experimental services 'hifi-ipfs'")

        row = layout.row()
        row.label(
            "to upload files to the ipfs. ")
        row = layout.row()

        row = layout.row()
        row = layout.row()
        row = layout.row()
        row.label(
            "You can put anything not used as your username.")

        row = layout.row()
        row.label(
            "Save both the name and token somewhere safe. You cannot recover it."
        )

        row = layout.row()
        row.label(
            'You cannot generate new tokens, if a username that has one already.'
        )
        row = layout.row()
        row = layout.row()
        row = layout.row()
        row.label(
            "These credential are 'hifi-ipfs' service specific and the 'hifi-ipfs' service ")
        row = layout.row()
        row.label(
            "set here only tracks what have been uploaded with the username."
        )
        row = layout.row()
        row.label(text="and where they can be found for convenience.  ")
        row = layout.row()
        row.label(
            "Anything uploaded in another service to the ipfs network cannot be tracked.")
        row = layout.row()
        row = layout.row()
        row = layout.row()
        row.label(
            text=": Anything you put into the IPFS is public for anyone", icon="ERROR")

        row = layout.row()
        row.label(
            "with the url to see and maybe be nearly impossible to remove after ")

        row = layout.row()
        row.label(
            "being distributed / accessed from a public 'ipfs' gateway, unless forgotten.")

        row = layout.row()
        row = layout.row()
        row = layout.row()
        row.label(
            "Are you sure you want to enable the choice to upload on Export? ")
        row = layout.row()
        row.label(
            "(Currently supports avatars only)")

        row = layout.row()

        row.prop(self, "agree")

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=600, height=400)

    def execute(self, context):
        user_preferences = context.preferences
        addon_prefs = user_preferences.addons[__name__].preferences
        if self.agree:
            addon_prefs["ipfs"] = True
        else:
            addon_prefs["ipfs"] = False

        return {'FINISHED'}

class AUTH_OT_MVT_TOOLSET_Message_Auth_Success(bpy.types.Operator):
    """ This Operator show the user that the authentication to the gateway was successful
    """
    bl_idname = "metaverse_toolset_messages.auth_success"
    bl_label = ""
    bl_options = {'REGISTER', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, even):
        wm = context.window_manager
        return wm.invoke_popup(self, width=400, height=600)

    def execute(self, context):
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.label(text="Success:", icon="FILE_TICK")
        row = layout.row()
        row.label(text="Authentication Success! ")
        row = layout.row()
        row.label(text="Remember to Save Your Settings")


class HifiAddOnPreferences(AddonPreferences):
    bl_idname = __name__

    colorspaces_on_save: BoolProperty(name="Correct Color Space on save",
                                                     description="Correct Texture Color spaces for materials prior to saving.",
                                                    default=True,
                                                    update=on_color_space_automation_update)

    oventool: StringProperty(name="Oven Tool path (EXPERIMENTAL)",
                                   description="Point this to the High Fidelity Oven tool",
                                   subtype="FILE_PATH")

    ipfs: BoolProperty(name="IPFS (EXPERIMENTAL)",
                        description="Enabled IPFS", update=on_server_update)

    gateway_server: StringProperty(name="HIFI-IPFS Server",
                                    description="API to upload files",
                                    default=default_gateway_server,
                                    update=on_server_update)

    gateway_username: StringProperty(name="HIFI-IPFS Username",
                                      description="Enter any Username for API", default="",
                                      update=on_server_update)

    oauth_required: BoolProperty(default=oauth_default)
    oauth_api: StringProperty(default=oauth_api, options={"HIDDEN"})

    hifi_oauth: StringProperty(name="Hifi OAuth Token",
                                description="Enter an Oauth Token with identity permissions", default="",
                                update=on_token_update)

    gateway_token: StringProperty(name="HIFI-IPFS Token",
                                   description="login to API", default="")

    message_box: StringProperty(
        name="Status", default="", options={"SKIP_SAVE"})

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "colorspaces_on_save")
        layout.prop(self, "oventool")

        if self.ipfs:
            layout.prop(self, "ipfs")
            layout.prop(self, "gateway_server")
            layout.prop(self, "gateway_username")

            if self.oauth_required:
                row = layout.row()
                row.prop(self, "hifi_oauth")

                if len(self.hifi_oauth) == 0:
                    row.operator("metaverse_toolset.open_token_link")
            else:
                row = layout.row()
                row.prop(self, "gateway_token")

                if len(self.gateway_token) == 0:
                    row.operator("metaverse_toolset.gateway_generate_token")

            if len(self.message_box):
                layout.prop(self, "message_box")
        else:
            layout.operator("metaverse_toolset.ipfs_feature_info")
        
        layout.operator(
            HELP_OT_MVT_TOOLSET_Open_Forum_Link.bl_idname, icon='HELP')


class AUTH_OT_MVT_TOOLSET_Open_Token_Link(bpy.types.Operator):
    """ This Operator to open a link to the High Fidelity OAUTH Token generation website.
    """
    bl_idname = "metaverse_toolset.open_token_link"
    bl_label = "Get Hifi Identity Token"

    def execute(self, context):

        user_preferences = context.preferences
        addon_prefs = user_preferences.addons[__name__].preferences

        if "oauth_api" not in addon_prefs:
            addon_prefs["oauth_api"] = oauth_api

        if "windows-default" in webbrowser._browsers:
            webbrowser.get("windows-default").open(addon_prefs["oauth_api"])
        else:
            webbrowser.open(addon_prefs["oauth_api"])

        return {'FINISHED'}


class AUTH_OT_MVT_TOOLSET_Gateway_Generate_Token(bpy.types.Operator):
    """ This Operator is used to generate a Gateway token using the High Fidelity OAUTH Token.
    """
    bl_idname = "metaverse_toolset.gateway_generate_token"
    bl_label = "Generate Token"

    def execute(self, context):

        on_token_update(self, context)

        # TODO: Suggest to save as token can only be generated once, until password is added to this.

        return {'FINISHED'}


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
    
    self.layout.operator(EXPORT_OT_MVT_TOOLSET_FBX.bl_idname, text="Hifi FBX (.fbx)")
    self.layout.operator(EXPORT_OT_MVT_TOOLSET_FST_Writer_Operator.bl_idname,
                         text="HiFi Avatar FST (.fst)")
   # self.layout.operator(EXPORT_OT_MVT_TOOLSET_Export_GLTF_JSON.bl_idname,
   #                      text="HiFi Metaverse Scene JSON / GLTF (.json/.glb/.glm)")
    self.layout.operator(EXPORT_OT_MVT_TOOLSET_Export_FBX_JSON.bl_idname,
                         text="HiFi Metaverse Scene JSON / FBX (.json/.fbx)")



class HELP_OT_MVT_TOOLSET_Open_Forum_Link(bpy.types.Operator):
    """ Helper Operator to open the forum post regarding this plugin """
    bl_idname = "metaverse_toolset.hf_open_forum_link"
    bl_label = "HF Forum Thread / Bug Reports"

    bl_region_type = "TOOLS"
    bl_space_type = "VIEW_3D"

    def execute(self, context):
        url = "https://forums.highfidelity.com/t/high-fidelity-blender-add-on-version-1-1-10-released/13717"
        if "windows-default" in webbrowser._browsers:
            webbrowser.get("windows-default").open(url)
        else:
            webbrowser.open(url)

        return {'FINISHED'}


classes = (
    EXPORT_OT_MVT_TOOLSET_Message_Error_Missing_ATP_Override,
    EXPORT_OT_MVT_TOOLSET_IPFS_Feature_Info,
    EXPORT_OT_MVT_TOOLSET_Export_GLTF_JSON,
    EXPORT_OT_MVT_TOOLSET_Export_FBX_JSON,
    EXPORT_OT_MVT_TOOLSET_FBX,
    IMPORT_OT_MVT_TOOLSET_Scene_From_JSON,
    HELP_OT_MVT_TOOLSET_Open_Forum_Link,
    AUTH_OT_MVT_TOOLSET_Open_Token_Link,
    AUTH_OT_MVT_TOOLSET_Gateway_Generate_Token,
    AUTH_OT_MVT_TOOLSET_Message_Auth_Success,
    HifiAddOnPreferences,
)

main_register, main_unregister = bpy.utils.register_classes_factory(classes)    
bpy.app.handlers.save_pre.append(utils.helpers.materials.correct_all_color_spaces_to_non_color)

existing_shapekey_merger = False
def register():
    main_register()
    scene_define()
    module_register()
    custom_register()
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
    scene_delete()
    module_unregister()
    custom_unregister()
    if  existing_shapekey_merger == False:
        bpy.utils.unregister_class(ApplyModifierForObjectWithShapeKeysOperator)

    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    ui.unregister_operators()


