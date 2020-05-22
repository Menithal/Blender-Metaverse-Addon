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

# Adding Armature related functions to the Blender Hifi Tool set
# Copyright 2019 Matti 'Menithal' Lahtinen

import sys
import bpy
import webbrowser
from bpy.props import StringProperty
from urllib.parse import urlencode
from mathutils import Quaternion, Vector, Euler, Matrix

import metaverse_tools

from metaverse_tools import default_gateway_server
from metaverse_tools.utils import bpyutil
from metaverse_tools.gateway import client as GatewayClient

from . import armature_tools
from . import texture_tools
from . import sculpt_tools
from . import pose_tools
from . import mesh_tools
from .modules import hifi as hifi_ui
from .modules import vrc as vrc_ui
from .modules import tu as tu_ui

category = "MVT: General Tools"

class EXPORT_OT_MVT_TOOLSET_IPFS_Assets_Toolset(bpy.types.Operator):
    """ Operator meant to open a browser to the current active ipfs gateway """
    bl_idname = "metaverse_toolset.hf_ipfs_assets_toolset"
    bl_label = "IPFS Uploads"

    bl_region_type = "TOOLS"
    bl_space_type = "VIEW_3D"

    def execute(self, context):
        user_preferences = context.preferences
        addon_prefs = user_preferences.addons[metaverse_tools.__name__].preferences

        if not "gateway_server" in addon_prefs.keys():
            addon_prefs["gateway_server"] = default_gateway_server

        server = addon_prefs["gateway_server"]

        browsers = webbrowser._browsers
        # Better way would be to use jwt, but this is just a proto
        routes = GatewayClient.routes(server)
        # TODO On failure this should return something else.

        path = routes["uploads"] + "?" + urlencode({'token': addon_prefs["gateway_token"],
                                                    'username': addon_prefs["gateway_username"]})
        if "windows-default" in browsers:
            print("Windows detected")
            webbrowser.get("windows-default").open(server + path)
        else:
            webbrowser.open(server + path)

        return {'FINISHED'}

# -----

class SAVE_OT_MVT_TOOLSET_Message_Remind_Save(bpy.types.Operator):
    """ Message to remind user to save their scene prior to continuing """
    bl_idname = "metaverse_toolset_messages.remind_save"
    bl_label = "Save scene to a blend file first allowing for relative directories."
    bl_options = {'REGISTER', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, even):
        print("Invoked")
        wm = context.window_manager
        return wm.invoke_popup(self, width=400, height=200)

    def execute(self, context):
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.label(text="Warning:", icon="ERROR")
        row = layout.row()
        row.label(text=self.bl_label)



class OBJECT_PT_MVT_TOOLSET_Assets_Display(bpy.types.Panel):
    """ Panel for IPFS-Gateway Asset related access tools """
    bl_label = "Assets"
    bl_region_type = "TOOLS"

    bl_space_type = "VIEW_3D"

    @classmethod
    def poll(self, context):
        user_preferences = context.preferences
        addon_prefs = user_preferences.addons[metaverse_tools.__name__].preferences
        return "gateway_token" in addon_prefs and len(addon_prefs["gateway_token"]) > 0

    def draw(self, context):
        layout = self.layout
        layout.operator(
            EXPORT_OT_MVT_TOOLSET_IPFS_Assets_Toolset.bl_idname, emboss=False)
        return None


class TEST_WT_workspace(bpy.types.WorkSpaceTool):
    bl_space_type = "VIEW_3D"
    bl_context_mode = "OBJECT"
    bl_idname = "metaverse_toolset.test"
    bl_label = "Boop"
    bl_category = "New Stuff"
    bl_description = (
        "This is\n"
        "A TeSt"
    )
    bl_icon = "ops.generic.select_circle"


classes = (
    OBJECT_PT_MVT_TOOLSET_Assets_Display,
    EXPORT_OT_MVT_TOOLSET_IPFS_Assets_Toolset,
    SAVE_OT_MVT_TOOLSET_Message_Remind_Save,
)


module_register, module_unregister = bpy.utils.register_classes_factory(
    classes)


def register_operators():
    module_register()
    armature_tools.module_register()
    pose_tools.module_register()
    texture_tools.module_register()
    hifi_ui.module_register()
    vrc_ui.module_register()
    tu_ui.module_register()
    mesh_tools.module_register()
    sculpt_tools.module_register()


def unregister_operators():
    module_unregister()
    armature_tools.module_unregister()
    pose_tools.module_unregister()
    texture_tools.module_register()
    hifi_ui.module_unregister()
    vrc_ui.module_unregister()
    tu_ui.module_unregister()
    mesh_tools.module_unregister()
    sculpt_tools.module_unregister()
