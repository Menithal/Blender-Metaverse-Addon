
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
from metaverse_tools.utils.helpers import materials
from metaverse_tools.armature import SkeletonTypes

category = "MVT: HiFi Tools"


class AVATAR_PT_MVT_metaverse_toolset(bpy.types.Panel):
    """ Panel for Vircadia Avatar related conversion tools """
    bl_label = "Vircadia Avatar Tools"
    bl_icon = "BONES_DATA"

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = category

    @classmethod
    def poll(self, context):
        return context.mode == "OBJECT"

    def draw(self, context):
        layout = self.layout
        layout.operator(
            ARMATURE_OT_MVT_TOOLSET_Create_HIFI_Operator.bl_idname, icon="OUTLINER_OB_ARMATURE")
        layout.operator(AVATAR_OT_MVT_TOOLSET_Convert_Custom_To_Hifi.bl_idname, icon="ARMATURE_DATA")
        layout.operator(AVATAR_OT_MVT_TOOLSET_Convert_MMD_To_Hifi.bl_idname, icon="ARMATURE_DATA")
        row = layout.row()
        row.operator(BONES_OT_MVT_TOOLSET_Pin_Problem_Bones.bl_idname, icon="PINNED")
        row.operator(BONES_OT_MVT_TOOLSET_Fix_Rolls.bl_idname, icon="CON_ROTLIKE")

        return None


class ARMATURE_OT_MVT_TOOLSET_Create_HIFI_Operator(bpy.types.Operator):
    """ Tool to quickly create a Hifi specific Avatar Skeleton """
    bl_idname = "metaverse_toolset.hf_create_armature"
    bl_label = "Add HiFi Armature"

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = category

    @classmethod
    def poll(self, context):
        return context.mode == "OBJECT"

    def execute(self, context):
        bones_builder.build_skeleton(SkeletonTypes.HIFI)
        return {'FINISHED'}


class AVATAR_OT_MVT_TOOLSET_Convert_Custom_To_Hifi(bpy.types.Operator):
    """ Converter to bind bones from a custom skeleton into a HF specific one. """
    bl_idname = "metaverse_toolset.hf_convert_custom_avatar"
    bl_label = "Custom Avatar"

    bl_icon = "BONES_DATA"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = category

    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # https://b3d.interplanety.org/en/creating-pop-up-panels-with-user-ui-in-blender-add-on/
        bpy.ops.metaverse_toolset.hf_open_custom_avatar_binder(
            'INVOKE_DEFAULT')
        return {'FINISHED'}


class AVATAR_OT_MVT_TOOLSET_Convert_MMD_To_Hifi(bpy.types.Operator):
    """ Converter to update an untranslated MMD avatar into a HF specific one. """
    bl_idname = "metaverse_toolset.hf_convert_mmd_avatar"
    bl_label = "MMD Avatar"

    bl_space_type = "VIEW_3D"
    bl_icon = "BONES_DATA"
    bl_region_type = "UI"
    bl_category = category

    def execute(self, context):
        mmd.convert_mmd_avatar_hifi()
        return {'FINISHED'}


class AVATAR_OT_MVT_TOOLSET_Convert_Mixamo_To_Hifi(bpy.types.Operator):
    """ Converter to update an Mixamo avatar into a HF specific one. """
    bl_idname = "metaverse_toolset.hf_convert_mixamo_avatar"
    bl_label = "Mixamo Avatar"

    bl_icon = "BONES_DATA"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = category

    def execute(self, context):
        mixamo.convert_mixamo_avatar_hifi()
        return {'FINISHED'}


class AVATAR_OT_MVT_TOOLSET_Convert_MakeHuman_To_Hifi(bpy.types.Operator):
    """ Converter to update an Makehuman avatar into a HF specific one. """
    bl_idname = "metaverse_toolset.hf_convert_makehuman_avatar"
    bl_label = "MakeHuman Avatar"

    bl_icon = "BONES_DATA"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = category

    def execute(self, context):
        makehuman.convert_makehuman_avatar_hifi()
        bones_builder.retarget_armature({'apply': True}, bpy.context.view_layer.objects)
        return {'FINISHED'}


class BONES_OT_MVT_TOOLSET_Pin_Problem_Bones(bpy.types.Operator):
    """ Correct Rolls AND Pins usually problemative bones to match the HF reference skeleton. """
    bl_idname = "metaverse_toolset.hf_pin_problem_bones"
    bl_label = "Pin Problem Bones"

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = category
    @classmethod
    def poll(self, context):
        return (context.mode == "OBJECT" or context.mode == "POSE") and (context.active_object is not None and context.active_object.type == "ARMATURE")

    def execute(self, context):
        for obj in bpy.context.view_layer.objects:
            if obj.type == "ARMATURE":
                skeleton_type = SkeletonTypes.get_type_from_armature(obj)
                # TODO: Should be expanded upon
                bones_builder.pin_common_bones(obj, False)

        return {'FINISHED'}


class BONES_OT_MVT_TOOLSET_Fix_Rolls(bpy.types.Operator):
    """ Corrects the Rolls to match the expected rolls of the skeleton bones in HF """
    bl_idname = "metaverse_toolset.hf_fix_bone_rolls"
    bl_label = "Match Reference Rolls"

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = category
    @classmethod
    def poll(self, context):
        return (context.mode == "OBJECT" or context.mode == "POSE") and (context.active_object is not None and context.active_object.type == "ARMATURE")

    def execute(self, context):
        selected = bpy.context.selected_objects

        if selected is None:
            selected = bpy.context.view_layer.objects

        bones_builder.find_select_armature_and_children(selected)

        selected = bpy.context.selected_objects

        bpy.ops.object.mode_set(mode="EDIT")

        if selected is None:
            selected = bpy.context.view_layer.objects

        for obj in selected:
            if obj.type == "ARMATURE":
                bpy.ops.object.mode_set(mode="EDIT")
                for ebone in obj.data.edit_bones:
                    bones_builder.correct_bone_rotations(ebone)

            bones_builder.correct_scale_rotation(obj, False)

        bpy.ops.object.mode_set(mode="OBJECT")
        bones_builder.clear_pose(selected)

        bpy.ops.object.mode_set(mode="OBJECT")

        return {'FINISHED'}


class SCENE_PT_MVT_TOOLSET(bpy.types.Panel):
    """ Panel for Scene related tools """
    bl_label = "Hifi Scene Tools"

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = category

    def draw(self, context):
        layout = self.layout
        layout.operator(
            SCENE_OT_MVT_TOOLSET_Fix_Hifi_Scene_Env_Rotation.bl_idname)

        return None


class SCENE_OT_MVT_TOOLSET_Fix_Hifi_Scene_Env_Rotation(bpy.types.Operator):
    """ Tool to Fix Environment Rotations in Blender to match how the would be in Hifi """
    bl_idname = "metaverse_toolset.hf_fix_scene_rotation"
    bl_label = "Match HF Env Rotation"

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = category

    def execute(self, context):
        materials.fix_env_rotations()
        return {"FINISHED"}

class BONES_OT_MVT_TOOLSET_Set_Physical(bpy.types.Operator):
    """ Sets names for the select bones to match the flow bone setup in HF """
    bl_idname = "metaverse_toolset.hf_set_physical_bones"
    bl_label = "Set Bone Physical"

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = category

    @classmethod
    def poll(self, context):
        return context.selected_bones is not None and len(context.selected_bones) > 0

    def execute(self, context):
        bones_builder.set_selected_bones_physical(context.selected_bones)
        return {'FINISHED'}


class BONES_OT_MVT_TOOLSET_Remove_Physical(bpy.types.Operator):
    """ Clears names for the select bones from matching the flow bone setup in HF """
    bl_idname = "metaverse_toolset.hf_remove_physical_bones"
    bl_label = "Remove Bone Physical"

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = category

    @classmethod
    def poll(self, context):
        return context.selected_bones is not None and len(context.selected_bones) > 0

    def execute(self, context):
        bones_builder.remove_selected_bones_physical(context.selected_bones)
        return {'FINISHED'}



classes = (
    AVATAR_PT_MVT_metaverse_toolset,
    ARMATURE_OT_MVT_TOOLSET_Create_HIFI_Operator,
    BONES_OT_MVT_TOOLSET_Fix_Rolls,
    BONES_OT_MVT_TOOLSET_Pin_Problem_Bones,
    BONES_OT_MVT_TOOLSET_Set_Physical,
    BONES_OT_MVT_TOOLSET_Remove_Physical,

    AVATAR_OT_MVT_TOOLSET_Convert_Custom_To_Hifi,
    # AVATAR_OT_MVT_TOOLSET_Convert_MakeHuman_To_Hifi,
    AVATAR_OT_MVT_TOOLSET_Convert_MMD_To_Hifi,
    # AVATAR_OT_MVT_TOOLSET_Convert_Mixamo_To_Hifi,
    SCENE_PT_MVT_TOOLSET,
    SCENE_OT_MVT_TOOLSET_Fix_Hifi_Scene_Env_Rotation
)


module_register, module_unregister = bpy.utils.register_classes_factory(
    classes)
