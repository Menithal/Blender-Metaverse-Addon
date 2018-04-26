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
import hifi_tools.utils.bones as bones
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

        FSTWriter.fst_export(self, to_export)

        return {'FINISHED'}
