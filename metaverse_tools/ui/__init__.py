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

import bpy
from bpy.props import StringProperty
from mathutils import Quaternion, Vector, Euler, Matrix

import metaverse_tools

from . import armature_tools
from . import texture_tools
from . import sculpt_tools
from . import pose_tools
from . import mesh_tools
from . import action_tools

from .modules import hifi as hifi_ui
from .modules import vrc as vrc_ui
from .modules import tu as tu_ui
from .modules import generic as generic_ui

category = "MVT: General Tools"

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


classes = (
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
    action_tools.module_register()
    mesh_tools.module_register()
    sculpt_tools.module_register()
    generic_ui.module_register()

def unregister_operators():
    module_unregister()
    armature_tools.module_unregister()
    pose_tools.module_unregister()
    texture_tools.module_unregister()
    hifi_ui.module_unregister()
    vrc_ui.module_unregister()
    tu_ui.module_unregister()
    action_tools.module_unregister()
    mesh_tools.module_unregister()
    sculpt_tools.module_unregister()
    generic_ui.module_unregister()
