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
# Copyright 2019 Matti 'Menithal' Lahtinen

import bpy
import os
import metaverse_tools

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
import metaverse_tools.files.fst.writer as FSTWriter
from metaverse_tools.utils.bones.bones_builder import find_armatures


class EXPORT_OT_MVT_TOOLSET_Message_Warn_Bone(bpy.types.Operator):
    """ This Operator is used to warn if the armature may have too many bones for it to work properly in High Fidelity.
    """
    bl_idname = "metaverse_toolset_messages.export_warn_bone"
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
        row.label(text="Avatar Successfully Exported: ")
        row = layout.row()
        row.label(text="Warning:", icon="QUESTION")
        row = layout.row()
        row.label(
            "You may have issues with the avatars pose not being streamed with")
        row = layout.row()
        row.label(text="So many bones.")
        row = layout.row()
        row.label(text="Try combining some if you have issues in metaverse_toolset.")


class EXPORT_OT_MVT_TOOLSET_Message_Error(bpy.types.Operator):
    """ This Operator is used show that there has been an error while exporting an avatar.
    """
    bl_idname = "metaverse_toolset_messages.export_error"
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
        row.label(text="Avatar Export Failed. Please Check the console logs")


class EXPORT_OT_MVT_TOOLSET_Message_Error_No_Armature(bpy.types.Operator):
    """ This Operator is used show that exported avatar is missing an armature
    """
    bl_idname = "metaverse_toolset_messages.export_error_no_armature"
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
        row.label(text="Avatar Export Failed. Please have 1 armature on selected")


class EXPORT_OT_MVT_TOOLSET_Message_Success(bpy.types.Operator):
    """ This Operator is used show that avatar was exported successfully
    """
    bl_idname = "metaverse_toolset_messages.export_success"
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
        row.label(text="Avatar Export Successful.")


class EXPORT_OT_MVT_TOOLSET_Hifi_FST_Writer_Operator(bpy.types.Operator, ExportHelper):
    """ This Operator exports a Vircadia compatible FST and FBX of the current avatar.
    """
    bl_idname = "metaverse_toolset.export_fst"
    bl_label = "Export Hifi Avatar"
    bl_options = {'UNDO'}

    directory: StringProperty()
    filename_ext = ".fst"

    # TODO: instead create a new directory instead of a file.

    filter_glob: StringProperty(default="*.fst", options={'HIDDEN'})
    selected_only: BoolProperty(
        default=False, name="Selected Only", description="Selected Only")

    #anim_graph_url = StringProperty(default="", name="Animation JSON Url",
    #                                description="Avatar Animation JSON absolute url path")

    script: StringProperty(default="", name="Avatar Script Path",
                            description="Avatar Script absolute url path, Script that is run on avatar")

    flow: BoolProperty(default=False, name="Add Flow Script",
                        description="Adds flow script template as an additional Avatar script")

    embed: BoolProperty(default=False, name="Embed Textures",
                         description="Embed Textures to Exported Model. Turn this off if you are having issues of Textures not showing correctly in elsewhere.")

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "selected_only")
       #layout.prop(self, "flow")
        layout.prop(self, "embed")

        #layout.prop(self, "anim_graph_url")
        layout.prop(self, "script")

    def execute(self, context):
        if not self.filepath:
            raise Exception("filepath not set")

        to_export = None

        if self.selected_only:
            to_export = list(bpy.context.selected_objects)
        else:
            to_export = list(bpy.context.view_layer.objects)

        print(to_export)
        
        self.scale = 1  # Add scene scale here

        armatures = find_armatures(to_export)
        if len(armatures) > 1 or len(armatures) == 0:
            bpy.ops.metaverse_toolset_messages.export_error_no_armature('INVOKE_DEFAULT')
            return {'CANCELLED'}

        val = FSTWriter.fst_export(self, to_export)
        
        if val == {'FINISHED'}:
            if len(armatures[0].data.edit_bones) > 100:
                bpy.ops.metaverse_toolset_messages.export_warn_bone('INVOKE_DEFAULT')
            else:
                bpy.ops.metaverse_toolset_messages.export_success('INVOKE_DEFAULT')
            return {'FINISHED'}
        else:
            bpy.ops.metaverse_toolset_messages.export_error('INVOKE_DEFAULT')
            return val


classes = (
    EXPORT_OT_MVT_TOOLSET_Hifi_FST_Writer_Operator,
    EXPORT_OT_MVT_TOOLSET_Message_Warn_Bone,
    EXPORT_OT_MVT_TOOLSET_Message_Error,
    EXPORT_OT_MVT_TOOLSET_Message_Error_No_Armature,
    EXPORT_OT_MVT_TOOLSET_Message_Success
) 

module_register, module_unregister = bpy.utils.register_classes_factory(classes)    
