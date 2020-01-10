
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

# Copyright 2020 Matti 'Menithal' Lahtinen

import bpy

from metaverse_tools.utils.bones import bones_builder, mmd, mixamo, makehuman
from metaverse_tools.utils.helpers import mesh
from metaverse_tools.armature import SkeletonTypes
from metaverse_tools.utils.bpyutil import move_bone_layer

from .hifi import BONES_OT_MVT_TOOLSET_Pin_Problem_Bones, BONES_OT_MVT_TOOLSET_Fix_Rolls


category = "MVT: TU Tools"

class AVATAR_PT_MVT_TU_TOOLSET(bpy.types.Panel):
    """ Panel for TU Avatar related tools """
    bl_label = "TU Avatar Tools"
    bl_icon = "BONES_DATA"

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = category

    @classmethod
    def poll(self, context):
        return context.mode == "OBJECT"

    def draw(self, context):
        layout = self.layout

        layout.operator(ARMATURE_OT_MVT_TOOLSET_Create_TU_Operator.bl_idname, icon="OUTLINER_OB_ARMATURE")

        row = layout.row()
        layout.operator(ARMATURE_OT_MVT_TOOLSET_Clear_Shapekeys.bl_idname, icon="OUTLINER_OB_LATTICE")
        row = layout.row()
        layout.operator(ARMATURE_OT_MVT_TOOLSET_Fix_common_TU_issues.bl_idname, icon="OUTLINER_OB_ARMATURE")


        row = layout.row()
        #row.operator(BONES_OT_MVT_TOOLSET_Pin_Problem_Bones.bl_idname, icon="PINNED")
        row.operator(BONES_OT_MVT_TOOLSET_Fix_Rolls.bl_idname, icon="CON_ROTLIKE")
        return None


class ARMATURE_OT_MVT_TOOLSET_Create_TU_Operator(bpy.types.Operator):
    """ Tool to quickly create a TU specific Avatar Skeleton """
    bl_idname = "metaverse_toolset.tu_create_armature"
    bl_label = "Add TU Armature"

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = category

    @classmethod
    def poll(self, context):
        return context.mode == "OBJECT"

    def execute(self, context):
        bpy.context.scene.unit_settings.scale_length = 0.01
        bpy.context.scene.unit_settings.system = 'METRIC'

        bones_builder.build_skeleton(SkeletonTypes.TU)

        # Change to edit mode (skeleton should be selected)
        
        bpy.ops.object.mode_set(mode="EDIT")
        # Go through bones 

        for ebone in bpy.context.active_object.data.edit_bones:
            print(ebone.name)
            if ebone.name == "root":
                print("Affect")
                move_bone_layer(ebone, 2)
            elif ebone.name.find("twist") is not -1:
                print("Affect")
                move_bone_layer(ebone, 2)

        bpy.ops.object.mode_set(mode="OBJECT")

        return {'FINISHED'}


        
class ARMATURE_OT_MVT_TOOLSET_Clear_Shapekeys(bpy.types.Operator):
    """ Tool to quickly Clean Shapekeys """
    bl_idname = "metaverse_toolset.tu_clean_shapekeys"
    bl_label = "Clean all Shapekeys" #Later will open a popup instead to select a method

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = category

    @classmethod
    def poll(self, context):
        return context.mode == "OBJECT" and context.active_object is not None and context.active_object.type == "MESH"

    def execute(self, context):
        # If object is armature then should go through parent
        bpy.ops.object.shape_key_remove(all=True)
        return {'FINISHED'}


        
class ARMATURE_OT_MVT_TOOLSET_Fix_common_TU_issues(bpy.types.Operator):
    """ Tool to fix common weight issues with TU """
    bl_idname = "metaverse_toolset.tu_fix_common_weight_issues"
    bl_label = "Fix Common Weight issues TU" #Later will open a popup instead to select a method

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = category

    @classmethod
    def poll(self, context):
        print(context.mode, context.active_object)
        return context.mode == "OBJECT" and context.active_object is not None and context.active_object.type == "MESH"

    def execute(self, context):   
        
        
        return {'FINISHED'}

def tu_fix_common(mesh, context):
    bpy.ops.object.mode_set(mode="EDIT")

    clear_groups = ['root', 'upperarm_twist_01_l', 'lowerarm_twist_01_l', 'lowerarm_twist_01_r', 'upperarm_twist_01_r']

    bpy.ops.mesh.select_all(action='SELECT')

    bpy.ops.object.vertex_group_lock(action="UNLOCK")

    for vertex in clear_groups:
        print(bpy.context.active_object.vertex_groups[vertex], vertex)
        bpy.context.active_object.vertex_groups[vertex].lock_weight = False
        bpy.ops.object.vertex_group_set_active(group=vertex)
        bpy.ops.object.vertex_group_remove_from()
        bpy.context.active_object.vertex_groups[vertex].lock_weight = True
        ##ASSIGN weight to 0

    bpy.ops.object.vertex_group_normalize_all(lock_active = False)

    bpy.ops.object.mode_set(mode="OBJECT")
    mesh.clean_unused_vertex_groups(context.active_object)

classes = (
    AVATAR_PT_MVT_TU_TOOLSET,
    ARMATURE_OT_MVT_TOOLSET_Create_TU_Operator,
    ARMATURE_OT_MVT_TOOLSET_Clear_Shapekeys,
    ARMATURE_OT_MVT_TOOLSET_Fix_common_TU_issues
)

module_register, module_unregister = bpy.utils.register_classes_factory(
    classes)
