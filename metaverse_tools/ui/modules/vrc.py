
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

from metaverse_tools.utils.bones import bones_builder, mmd, mixamo, makehuman
from metaverse_tools.utils.helpers import mesh
from metaverse_tools.armature import SkeletonTypes
#temporary
from .hifi import BONES_OT_MVT_TOOLSET_Pin_Problem_Bones, BONES_OT_MVT_TOOLSET_Fix_Rolls

category = "MVT: VRC Tools"

expected_vrc_shapekeys = [
    'vrc.blink_left',
    'vrc.blink_right',
    'vrc.lowerlid_left',
    'vrc.lowerlid_right',
    'vrc.v_aa',
    'vrc.v_ch',
    'vrc.v_dd',
    'vrc.v_e',
    'vrc.v_ff',
    'vrc.v_ih',
    'vrc.v_kk',
    'vrc.v_nn',
    'vrc.v_oh',
    'vrc.v_ou',
    'vrc.v_pp',
    'vrc.v_rr',
    'vrc.v_sil',
    'vrc.v_ss',
    'vrc.v_th',
]


class AVATAR_PT_MVT_VRC_TOOLSET(bpy.types.Panel):
    """ Panel for TU Avatar related tools """
    bl_label = "VRC Avatar Tools"
    bl_icon = "BONES_DATA"

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = category

    @classmethod
    def poll(self, context):
        return context.mode == "OBJECT"

    def draw(self, context):
        layout = self.layout

        layout.operator(ARMATURE_OT_MVT_TOOLSET_Create_VRC_Operator.bl_idname, icon="OUTLINER_OB_ARMATURE")
        layout.operator(ARMATURE_OT_MVT_TOOLSET_Generate_Empty_VRC_Shapekeys.bl_idname, icon="MESH_MONKEY")
        layout.operator(ARMATURE_OT_MVT_TOOLSET_Sort_VRC_Shapekeys.bl_idname, icon="SORTSIZE")
        row = layout.row()

        #row.operator(BONES_OT_MVT_TOOLSET_Pin_Problem_Bones.bl_idname, icon="PINNED")
        row.operator(BONES_OT_MVT_TOOLSET_Fix_Rolls.bl_idname, icon="CON_ROTLIKE")
        return None


class ARMATURE_OT_MVT_TOOLSET_Create_VRC_Operator(bpy.types.Operator):
    """ Tool to quickly create a VRC specific Avatar Skeleton """
    bl_idname = "metaverse_toolset.vrc_create_armature"
    bl_label = "Add VRC Armature"

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = category

    @classmethod
    def poll(self, context):
        return context.mode == "OBJECT"

    def execute(self, context):
        bones_builder.build_skeleton(SkeletonTypes.VRC)
        return {'FINISHED'}


class ARMATURE_OT_MVT_TOOLSET_Generate_Empty_VRC_Shapekeys(bpy.types.Operator):
    """ Tool to generate (Empty) Shapekeys for VRC """
    bl_idname = "metaverse_toolset.vrc_generate_empty_shapekeys"
    bl_label = "Generate VRC Shapekeys" #Later will open a popup instead to select a method

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = category

    @classmethod
    def poll(self, context):
        return context.mode == "OBJECT" and context.active_object is not None and context.active_object.type == "MESH"

    def execute(self, context):
        mesh.generate_empty_shapekeys(context.active_object, expected_vrc_shapekeys)
        return {'FINISHED'}


class ARMATURE_OT_MVT_TOOLSET_Sort_VRC_Shapekeys(bpy.types.Operator):
    """ Tool to reorder Shapekeys for VRC """
    bl_idname = "metaverse_toolset.vrc_sort_shapekeys"
    bl_label = "Sort Shapekeys"

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = category

    @classmethod
    def poll(self, context):
        return context.mode == "OBJECT" and context.active_object is not None and context.active_object.type == "MESH" and len(mesh.get_shape_keys(context.active_object)) > 0

    def execute(self, context):
        mesh.sort_shapekeys(bpy.context.active_object, expected_vrc_shapekeys)
        return {'FINISHED'}





# Tools To Make

# Generate Shapekeys Drop Down
#   Empties: 
#   Based On Existing:
#   Copy And Mirror Current Shapekey
#   Drop Down but using CATS 


# Pin Problem Bones
#   Pins Eye Rotations and Upper Legs to match rotation of Hips


# Fix Common issues
#   Check If Valid Shapekey order
#   Check If Valid Body Name
#   Check if sil (silence matches basis)
#   Pin Problem Bones
#   Rescale
#   Check If Double Eyes
# Check If OTHER modifiers and Shapekeys (If so, then make sure to warn user.)


classes = (
    AVATAR_PT_MVT_VRC_TOOLSET,
    ARMATURE_OT_MVT_TOOLSET_Create_VRC_Operator,
    ARMATURE_OT_MVT_TOOLSET_Generate_Empty_VRC_Shapekeys,
    ARMATURE_OT_MVT_TOOLSET_Sort_VRC_Shapekeys,
)

module_register, module_unregister = bpy.utils.register_classes_factory(
    classes)
