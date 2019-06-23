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

import hifi_tools
from hifi_tools import default_gateway_server
from hifi_tools.utils import bpyutil
from hifi_tools.utils.bones import bones_builder, mmd, mixamo, makehuman
from hifi_tools.utils.helpers import materials
from hifi_tools.gateway import client as GatewayClient
from hifi_tools.armature.skeleton import structure as base_armature

from hifi_tools.armature.debug_armature_extract import armature_debug


class OBJECT_PT_HIFI_Toolset(bpy.types.Panel):
   # bl_idname = "OBJECT_PT_HIFI_Toolset"
    bl_label = "General Tools"
    bl_icon = "OBJECT_DATA"

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "High Fidelity"

    @classmethod
    def poll(self, context):
        return context.mode == "OBJECT" or context.mode == "POSE"

    def draw(self, context):
        layout = self.layout
        layout.operator(ARMATURE_OT_HIFI_Create_Operator.bl_idname)

        row = layout.row()
        row.operator(ARMATURE_OT_HIFI_Set_Rest_Pose_Operator.bl_idname)
        row.operator(ARMATURE_OT_HIFI_Clear_Rest_Pose_Operator.bl_idname)

        layout.operator(OBJECT_OT_HIFI_Fix_Scale_Operator.bl_idname)
        layout.operator(HELP_OT_HIFI_Open_Forum_Link.bl_idname)
        # layout.operator(HifiDebugArmatureOperator.bl_idname)
        # layout.operator(HifiArmatureRetargetPoseOperator.bl_idname)
        return None


class BONES_PT_HIFI_Toolset(bpy.types.Panel):
   # bl_idname = "BONES_PT_HIFI_Toolset"
    bl_label = "Bones Tools"
    bl_icon = "BONE_DATA"

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "High Fidelity"

    @classmethod
    def poll(self, context):
        return context.mode == "EDIT_ARMATURE"

    def draw(self, context):
        layout = self.layout
        layout.operator(BONES_OT_HIFI_Set_Physical.bl_idname)
        layout.operator(BONES_OT_HIFI_Remove_Physical.bl_idname)
        layout.operator(BONES_OT_HIFI_Combine.bl_idname)
        layout.operator(BONES_OT_HIFI_Combine_Disconnected.bl_idname)
        layout.operator(BONES_OT_HIFI_Connect_Selected.bl_idname)
        layout.operator(BONES_OT_HIFI_Disconnect_Selected.bl_idname)
        return None


class AVATAR_PT_HIFI_Toolset(bpy.types.Panel):
    #bl_idname = "AVATAR_PT_HIFI_Toolset"
    bl_label = "Avatar Converters"
    bl_icon = "BONES_DATA"

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "High Fidelity"

    @classmethod
    def poll(self, context):
        return context.mode == "OBJECT"

    def draw(self, context):
        layout = self.layout
        layout.operator(AVATAR_OT_HIFI_Convert_Custom.bl_idname)
        layout.operator(AVATAR_OT_HIFI_Convert_MMD.bl_idname)
        layout.operator(AVATAR_OT_HIFI_Convert_Mixamo.bl_idname)
        # layout.operator(HifiMakeHumanOperator.bl_idname)
        row = layout.row()

        row.operator(BONES_OT_HIFI_Pin_Problem_Bones.bl_idname)
        row.operator(BONES_OT_HIFI_Fix_Rolls.bl_idname)

        return None


class MATERIALS_PT_HIFI_Toolset(bpy.types.Panel):
   # bl_idname = "MATERIALS_PT_HIFI_Toolset"
    bl_label = "Material Tools"

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "High Fidelity"

    @classmethod
    def poll(self, context):
        return context.mode == "OBJECT"

    def draw(self, context):
        layout = self.layout

        # layout.operator(HifiMaterialFullbrightOperator.bl_idname)
        layout.operator(TEXTURES_OT_HIFI_Convert_To_Png.bl_idname)
        layout.operator(TEXTURES_OT_HIFI_Convert_To_Mask.bl_idname)
        layout.operator(MATERIALS_OT_HIFI_Correct_ColorData.bl_idname)
        return None


class OBJECT_PT_HIFI_Assets_Display(bpy.types.Panel):
    #bl_idname = "OBJECT_PT_HIFI_Assets_Display"
    bl_label = "Assets"

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "High Fidelity"

    @classmethod
    def poll(self, context):
        user_preferences = context.preferences
        addon_prefs = user_preferences.addons[hifi_tools.__name__].preferences
        return "gateway_token" in addon_prefs and len(addon_prefs["gateway_token"]) > 0

    def draw(self, context):
        layout = self.layout
        layout.operator(EXPORT_OT_HIFI_IPFS_Assets_Toolset.bl_idname)
        return None


class EXPORT_OT_HIFI_IPFS_Assets_Toolset(bpy.types.Operator):
    bl_idname = "hifi.ipfs_assets_toolset"
    bl_label = "IPFS Uploads"

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "High Fidelity"

    def execute(self, context):
        user_preferences = context.preferences
        addon_prefs = user_preferences.addons[hifi_tools.__name__].preferences

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


class ARMATURE_OT_HIFI_Create_Operator(bpy.types.Operator):
    
    bl_idname = "hifi.create_armature"
    bl_label = "Add HiFi Armature"

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "High Fidelity"

    @classmethod
    def poll(self, context):
        return context.mode == "OBJECT"

    def execute(self, context):
        bones_builder.build_skeleton()
        return {'FINISHED'}

# Remove once fst export is available


class ARMATURE_OT_HIFI_Set_Rest_Pose_Operator(bpy.types.Operator):
    bl_idname = "hifi.set_armature_rest_pose"
    bl_label = "Rest TPose"

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "High Fidelity"

    def execute(self, context):
        bones_builder.retarget_armature({'apply': False}, bpy.data.objects)
        return {'FINISHED'}


class ARMATURE_OT_HIFI_Clear_Rest_Pose_Operator(bpy.types.Operator):
    bl_idname = "hifi.clear_armature_rest_pose"
    bl_label = "Clear Pose"

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "High Fidelity"

    def execute(self, context):
        bones_builder.clear_pose(bpy.data.objects)
        return {'FINISHED'}


class OBJECT_OT_HIFI_Fix_Scale_Operator(bpy.types.Operator):
    bl_idname = "hifi.objects_fix_scale_and_rotation"
    bl_label = "Fix Scale and Rotations"

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "High Fidelity"

    def execute(self, context):

        for selected in context.selected_objects:
            bones_builder.correct_scale_rotation(selected, True)

        return {'FINISHED'}


class BONES_OT_HIFI_Pin_Problem_Bones(bpy.types.Operator):
    bl_idname = "hifi.pin_problem_bones"
    bl_label = "Pin Problem Bones"

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "High Fidelity"

    def execute(self, context):
        bpy.ops.object.mode_set(mode="EDIT")

        for obj in bpy.data.objects:
            if obj.type == "ARMATURE":
                bones_builder.pin_common_bones(obj, False)

        bpy.ops.object.mode_set(mode="OBJECT")
        return {'FINISHED'}


class BONES_OT_HIFI_Fix_Rolls(bpy.types.Operator):
    bl_idname = "hifi.fix_bone_rolls"
    bl_label = "Match Reference Rolls"

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "High Fidelity"

    def execute(self, context):
        bpy.ops.object.mode_set(mode="EDIT")

        selected = bpy.context.selected_objects
        if selected is None:
            selected = bpy.data.objects

        for obj in selected:
            if obj.type == "ARMATURE":
                print("Lets Do this shit ", obj)
                bpy.ops.object.mode_set(mode="OBJECT")
                bones_builder.correct_scale_rotation(obj, False)
                bpy.ops.object.mode_set(mode="EDIT")
                for ebone in obj.data.edit_bones:
                    bones_builder.correct_bone_rotations(ebone)

        bpy.ops.object.mode_set(mode="OBJECT")
        bones_builder.clear_pose(selected)

        bpy.ops.object.mode_set(mode="OBJECT")
        return {'FINISHED'}


# Remove once fst export is available
class BONES_OT_HIFI_Set_Physical(bpy.types.Operator):
    bl_idname = "hifi.set_physical_bones"
    bl_label = "Set Bone Physical"

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "High Fidelity"

    @classmethod
    def poll(self, context):
        return context.selected_bones is not None and len(context.selected_bones) > 0

    def execute(self, context):
        bones_builder.set_selected_bones_physical(context.selected_bones)
        return {'FINISHED'}

# Remove once fst export is available


class BONES_OT_HIFI_Remove_Physical(bpy.types.Operator):
    bl_idname = "hifi.remove_physical_bones"
    bl_label = "Remove Bone Physical"

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "High Fidelity"

    @classmethod
    def poll(self, context):
        return context.selected_bones is not None and len(context.selected_bones) > 0

    def execute(self, context):
        bones_builder.remove_selected_bones_physical(context.selected_bones)
        return {'FINISHED'}


class BONES_OT_HIFI_Combine(bpy.types.Operator):
    bl_idname = "hifi.combine_bones"
    bl_label = "Combine Bones"

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "High Fidelity"

    @classmethod
    def poll(self, context):
        return context.selected_bones is not None and len(context.selected_bones) > 1

    def execute(self, context):

        use_mirror_x = bpy.context.object.data.use_mirror_x
        bpy.context.object.data.use_mirror_x = False
        bones_builder.combine_bones(list(context.selected_bones),
                                    context.active_bone, context.active_object)
        bpy.context.object.data.use_mirror_x = use_mirror_x
        return {'FINISHED'}


class BONES_OT_HIFI_Connect_Selected(bpy.types.Operator):
    bl_idname = "hifi.connect_selected_bones"
    bl_label = "Connect Selected "

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "High Fidelity"

    def execute(self, context):
        bones_builder.bone_connection(context.selected_editable_bones, True)
        return {'FINISHED'}


class BONES_OT_HIFI_Disconnect_Selected(bpy.types.Operator):
    bl_idname = "hifi.disconnect_selected_bones"
    bl_label = "Disconnect Selected "

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "High Fidelity"

    def execute(self, context):
        bones_builder.bone_connection(context.selected_editable_bones, False)
        return {'FINISHED'}


class BONES_OT_HIFI_Combine_Disconnected(bpy.types.Operator):
    bl_idname = "hifi.combine_detached_bones"
    bl_label = "Combine Bones Detached"

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "High Fidelity"

    @classmethod
    def poll(self, context):
        return context.selected_bones is not None and len(context.selected_bones) > 1

    def execute(self, context):

        use_mirror_x = bpy.context.object.data.use_mirror_x
        bpy.context.object.data.use_mirror_x = False
        bones_builder.combine_bones(list(context.selected_bones),
                                    context.active_bone, context.active_object, False)
        bpy.context.object.data.use_mirror_x = use_mirror_x
        return {'FINISHED'}


class AVATAR_OT_HIFI_Convert_Custom(bpy.types.Operator):
    bl_idname = "hifi.convert_custom_avatar"
    bl_label = "Custom Avatar"

    bl_icon = "BONES_DATA"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "High Fidelity"

    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
            # https://b3d.interplanety.org/en/creating-pop-up-panels-with-user-ui-in-blender-add-on/
        bpy.ops.hifi.open_custom_avatar_binder('INVOKE_DEFAULT')
        return {'FINISHED'}


class AVATAR_OT_HIFI_Convert_MMD(bpy.types.Operator):
    bl_idname = "hifi.convert_mmd_avatar"
    bl_label = "MMD Avatar"

    bl_space_type = "VIEW_3D"
    bl_icon = "BONES_DATA"
    bl_region_type = "UI"
    bl_category = "High Fidelity"

    def execute(self, context):
        mmd.convert_mmd_avatar_hifi()
        return {'FINISHED'}


class AVATAR_OT_HIFI_Convert_Mixamo(bpy.types.Operator):
    bl_idname = "hifi.convert_mixamo_avatar"
    bl_label = "Mixamo Avatar"

    bl_icon = "BONES_DATA"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "High Fidelity"

    def execute(self, context):
        mixamo.convert_mixamo_avatar_hifi()
        return {'FINISHED'}


class AVATAR_OT_HIFI_Convert_MakeHuman(bpy.types.Operator):
    bl_idname = "hifi.convert_makehuman_avatar"
    bl_label = "MakeHuman Avatar"

    bl_icon = "BONES_DATA"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "High Fidelity"

    def execute(self, context):
        makehuman.convert_makehuman_avatar_hifi()
        bones_builder.retarget_armature({'apply': True}, bpy.data.objects)
        return {'FINISHED'}


class TEXTURES_OT_HIFI_Convert_To_Png(bpy.types.Operator):
    bl_idname = "hifi.convert_textures_to_png"
    bl_label = "Textures to PNG"

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "High Fidelity"

    def execute(self, context):
        materials.convert_to_png(bpy.data.images)
        return {'FINISHED'}


# Probably Depricated soon
class TEXTURES_OT_HIFI_Convert_To_Mask(bpy.types.Operator):
    bl_idname = "hifi.convert_textures_to_masked"
    bl_label = "Textures to Masked"

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "High Fidelity"

    def execute(self, context):
        materials.convert_images_to_mask(bpy.data.images)
        return {'FINISHED'}


# -----

class SAVE_OT_HIFI_Message_Remind_Save(bpy.types.Operator):
    bl_idname = "hifi_messages.remind_save"
    bl_label = "You must save scene to a blend file first allowing for relative directories."
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


class MATERIALS_OT_HIFI_Correct_ColorData(bpy.types.Operator):
    bl_idname = "hifi.correct_colordata"
    bl_label = "Set Non-Diffuse ColorData to None"

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "High Fidelity"

    def execute(self, context):
        materials.correct_all_color_spaces_to_non_color(context)
        return {'FINISHED'}


class HELP_OT_HIFI_Open_Forum_Link(bpy.types.Operator):
    bl_idname = "hifi.open_forum_link"
    bl_label = "Forum Thread / Bug Reports"

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "High Fidelity"

    def execute(self, context):
        url = "https://forums.highfidelity.com/t/high-fidelity-blender-add-on-version-1-1-10-released/13717"
        if "windows-default" in webbrowser._browsers:
            webbrowser.get("windows-default").open(url)
        else:
            webbrowser.open(url)

        return {'FINISHED'}


class BONES_OT_HIFI_Debug_Armature_Operator(bpy.types.Operator):
    bl_idname = "hifi.debug_armature"
    bl_label = "debug armature"

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "High Fidelity"

    def execute(self, context):
        armature_debug()
        return {'FINISHED'}


classes = (
    OBJECT_PT_HIFI_Toolset,
    BONES_PT_HIFI_Toolset,
    AVATAR_PT_HIFI_Toolset,

    MATERIALS_PT_HIFI_Toolset,
    OBJECT_PT_HIFI_Assets_Display,

    EXPORT_OT_HIFI_IPFS_Assets_Toolset,
    
    ARMATURE_OT_HIFI_Create_Operator,
    ARMATURE_OT_HIFI_Set_Rest_Pose_Operator,
    ARMATURE_OT_HIFI_Clear_Rest_Pose_Operator,
    
    BONES_OT_HIFI_Set_Physical,
    BONES_OT_HIFI_Remove_Physical,
    BONES_OT_HIFI_Combine,
    BONES_OT_HIFI_Combine_Disconnected,
    BONES_OT_HIFI_Connect_Selected,
    BONES_OT_HIFI_Fix_Rolls,
    BONES_OT_HIFI_Pin_Problem_Bones,
    
    AVATAR_OT_HIFI_Convert_Custom,
    #AVATAR_OT_HIFI_Convert_MakeHuman,
    AVATAR_OT_HIFI_Convert_MMD,
    AVATAR_OT_HIFI_Convert_Mixamo,

    MATERIALS_OT_HIFI_Correct_ColorData,
    TEXTURES_OT_HIFI_Convert_To_Png,
    TEXTURES_OT_HIFI_Convert_To_Mask,

    OBJECT_OT_HIFI_Fix_Scale_Operator,
    SAVE_OT_HIFI_Message_Remind_Save,
    
    HELP_OT_HIFI_Open_Forum_Link,
    
   # DebugArmatureOperator,
)


module_register, module_unregister = bpy.utils.register_classes_factory(
    classes)


def armature_create_menu_func(self, context):
    self.layout.operator("ARMATURE_OT_HIFI_Create_Operator",
                         text="Add HiFi Armature",
                         icon="BONES_DATA")


def register():
    print("Full Panel Register")
    module_register()


def unregister():
    print("Full Panel unRegister")
    module_unregister()
