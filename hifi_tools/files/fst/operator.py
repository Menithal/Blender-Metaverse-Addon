# -*- coding: utf-8 -*-
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
# Created by Matti 'Menithal' Lahtinen

import bpy
import os
import hifi_tools

from bpy_extras.io_utils import (
    ImportHelper,
    ExportHelper
)

from bpy.props import (
    StringProperty,
    BoolProperty,
    FloatProperty,
    EnumProperty
)
import hifi_tools.files.fst.writer as FSTWriter

from hifi_tools.utils.bones import find_armature


class HifiBoneOperator(bpy.types.Operator):
    bl_idname = "hifi_warn.bone_count"
    bl_label = ""
    bl_options = {'REGISTER', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, even):
        print("Invoked")
        wm = context.window_manager
        return wm.invoke_popup(self, width=400, height=600)

    def execute(self, context):
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.label("Avatar Successfully Exported: ")
        row = layout.row()
        row.label(text="Warning:", icon="QUESTION")
        row = layout.row()
        row.label(
            "You may have issues with the avatars pose not being streamed with")
        row = layout.row()
        row.label("So many bones.")
        row = layout.row()
        row.label("Try combining some if you have issues in HiFi.")


class HifiExportErrorOperator(bpy.types.Operator):
    bl_idname = "hifi_error.export"
    bl_label = ""
    bl_options = {'REGISTER', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, even):
        print("Invoked")
        wm = context.window_manager
        return wm.invoke_popup(self, width=400, height=600)

    def execute(self, context):
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.label(text="Warning:", icon="ERROR")
        row = layout.row()
        row.label("Avatar Export Failed. Please Check the console logs")


class HifiExportSucccessOperator(bpy.types.Operator):
    bl_idname = "hifi_success.export"
    bl_label = ""
    bl_options = {'REGISTER', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, even):
        print("Invoked")
        wm = context.window_manager
        return wm.invoke_popup(self, width=400, height=600)

    def execute(self, context):
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.label(text="Success:", icon="FILE_TICK")
        row = layout.row()
        row.label("Avatar Export Successful.")


class FSTWriterOperator(bpy.types.Operator, ExportHelper):
    bl_idname = "export_avatar.hifi_fbx_fst"
    bl_label = "Export Hifi Avatar"
    bl_options = {'UNDO'}

    directory = StringProperty()
    filename_ext = ".fst"

    filter_glob = StringProperty(default="*.fst", options={'HIDDEN'})
    selected_only = BoolProperty(
        default=False, name="Selected Only", description="Selected Only")

    embed = BoolProperty(default=False, name="Embed Textures",
                         description="Embed Textures to Exported Model")

    bake = BoolProperty(default=False, name="Oven Bake (Experimental)",
                        description="Use the HiFi Oven Tool to bake")

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "selected_only")
        layout.prop(self, "embed")
        oven_tool = context.user_preferences.addons[hifi_tools.__name__].preferences.oventool

        if(oven_tool is not None and "oven" in oven_tool):
            layout.prop(self, "bake")

    def execute(self, context):
        if not self.filepath:
            raise Exception("filepath not set")

        preferences = bpy.context.user_preferences.addons[hifi_tools.__name__].preferences

        if self.bake and (preferences.oventool is None or "oven" not in preferences.oventool):
            raise Exception(
                "Please set the oven path for the plugin. eg <pathToHighFidelity>/oven.exe")

        to_export = None

        if self.selected_only:
            to_export = list(bpy.context.selected_objects)
        else:
            to_export = list(bpy.data.objects)

        self.scale = 1  # Add scene scale here

        armature = find_armature(to_export)

        val = FSTWriter.fst_export(self, to_export)
        print(val)
        if val == {'FINISHED'}:
            if len(armature.data.edit_bones) > 100:
                bpy.ops.hifi_warn.bone_count('INVOKE_DEFAULT')
            else:
                bpy.ops.hifi_success.export('INVOKE_DEFAULT')
            return {'FINISHED'}
        else:
            bpy.ops.hifi_error.export('INVOKE_DEFAULT')
            return val
