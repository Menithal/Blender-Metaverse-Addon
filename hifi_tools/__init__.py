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
    "name": "HiFi Blender Add-on (gateway IPFS Integration)",
    "author": "Matti 'Menithal' Lahtinen",
    "version": (1, 1, 1),
    "blender": (2, 7, 7),
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

from . import armature
from . import utils
from . import world
from . import files

from .files.hifi_json.operator import *
from .files.fst.operator import *

from .gateway import client as GatewayClient

import bpy

from bpy.types import AddonPreferences

default_gateway_server="http://10.0.0.200"
                                     # default="http://theden.dyndns-home.com:8070"
class HifiAddOnPreferences(AddonPreferences):
    bl_idname = __name__
    oventool = StringProperty(name="Oven Tool path (EXPERIMENTAL)",
                                   description="Point this to the High Fidelity Oven tool",
                                   subtype="FILE_PATH")
    gateway_server = StringProperty(name="gateway Server",
                                     description="API to upload files",
                                     default=default_gateway_server
                                     )
    gateway_username = StringProperty(name="gateway IPFS Username",
                                       description="Username to API")
    gateway_token = StringProperty(name="gateway IPFS Token",
                                    description="login to API")

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "oventool")
        layout.prop(self, "gateway_server")
        layout.prop(self, "gateway_username")
        layout.prop(self, "gateway_token")
    
        if len(self.gateway_token) == 0:
            layout.operator(GatewayGenerateToken.bl_idname)


class GatewayGenerateToken(bpy.types.Operator):
    bl_idname = "gateway.generate_token"
    bl_label = "Generate Token"

    def execute(self, context):
        # gatewayClient.new_token()
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__name__].preferences

        username = addon_prefs["gateway_username"]

        if not "gateway_server" in addon_prefs.keys():
            addon_prefs["gateway_server"] = default_gateway_server

        server = addon_prefs["gateway_server"]          

        result = GatewayClient.new_token(server, username)
        
        if result is "Err":
            return {'CANCELLED'}
            
        addon_prefs["gateway_token"] = result

        #TODO: Suggest to save as token can only be generated once, until password is added to this.

        return {'FINISHED'}


if "add_mesh_extra_objects" not in addon_utils.addons_fake_modules:
    print(" Could not find add_mesh_extra_objects, Trying to add it automatically. Otherwise install it first via Blender Add Ons")
    addon_utils.enable("add_mesh_extra_objects")


def reload_module(name):
    if name in sys.modules:
        del sys.modules[name]


def menu_func_import(self, context):
    self.layout.operator(JSONLoaderOperator.bl_idname,
                         text="HiFi Metaverse Scene JSON (.json)")


def menu_func_export(self, context):
    self.layout.operator(FSTWriterOperator.bl_idname,
                         text="HiFi Avatar FST (.fst)")
    self.layout.operator(JSONWriterOperator.bl_idname,
                         text="HiFi Metaverse Scene JSON / FBX (.json/.fbx)")


def register():
    bpy.utils.register_module(__name__)  # Magic Function!
    bpy.types.INFO_MT_file_import.append(menu_func_import)
    bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()
