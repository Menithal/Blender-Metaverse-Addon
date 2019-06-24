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
from hifi_tools.utils.helpers import materials, mesh
from hifi_tools.gateway import client as GatewayClient
from hifi_tools.armature.skeleton import structure as base_armature
from hifi_tools.armature.debug_armature_extract import armature_debug


class OBJECT_PT_METAV_TOOLSET(bpy.types.Panel):
    """ Panel for Object related tools """
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
        layout.operator(ARMATURE_OT_METAV_TOOLSET_Create_Operator.bl_idname)

        row = layout.row()
        row.operator(
            ARMATURE_OT_METAV_TOOLSET_Set_Rest_Pose_Operator.bl_idname)
        row.operator(
            ARMATURE_OT_METAV_TOOLSET_Clear_Rest_Pose_Operator.bl_idname)

        layout.operator(OBJECT_OT_METAV_TOOLSET_Fix_Scale_Operator.bl_idname)
        layout.operator(HELP_OT_METAV_TOOLSET_Open_Forum_Link.bl_idname)
        # layout.operator(HifiDebugArmatureOperator.bl_idname)
        # layout.operator(HifiArmatureRetargetPoseOperator.bl_idname)
        return None


class BONES_PT_METAV_TOOLSET(bpy.types.Panel):
    """ Panel for Bone related tools """
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
        layout.operator(BONES_OT_METAV_TOOLSET_Set_Physical.bl_idname)
        layout.operator(BONES_OT_METAV_TOOLSET_Remove_Physical.bl_idname)
        layout.operator(BONES_OT_METAV_TOOLSET_Combine.bl_idname)
        layout.operator(BONES_OT_METAV_TOOLSET_Combine_Disconnected.bl_idname)
        layout.operator(BONES_OT_METAV_TOOLSET_Connect_Selected.bl_idname)
        layout.operator(BONES_OT_METAV_TOOLSET_Disconnect_Selected.bl_idname)
        return None


class AVATAR_PT_METAV_TOOLSET(bpy.types.Panel):
    """ Panel for HF Avatar related conversion tools """
    bl_label = "Avatar Converters for HF"
    bl_icon = "BONES_DATA"

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "High Fidelity"

    @classmethod
    def poll(self, context):
        return context.mode == "OBJECT"

    def draw(self, context):
        layout = self.layout
        layout.operator(AVATAR_OT_METAV_TOOLSET_Convert_Custom.bl_idname)
        layout.operator(AVATAR_OT_METAV_TOOLSET_Convert_MMD.bl_idname)
        # layout.operator(AVATAR_OT_METAV_TOOLSET_Convert_Mixamo.bl_idname)
        # layout.operator(HifiMakeHumanOperator.bl_idname)
        row = layout.row()

        row.operator(BONES_OT_METAV_TOOLSET_Pin_Problem_Bones.bl_idname)
        row.operator(BONES_OT_METAV_TOOLSET_Fix_Rolls.bl_idname)

        return None


class MATERIALS_PT_METAV_TOOLSET(bpy.types.Panel):
    """ Panel for Material related tools """
    bl_label = "Material Tools"

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "High Fidelity"

    @classmethod
    def poll(self, context):
        return context.mode == "OBJECT"

    def draw(self, context):
        layout = self.layout

        layout.operator(TEXTURES_OT_METAV_TOOLSET_Convert_To_Png.bl_idname)
        layout.operator(TEXTURES_OT_METAV_TOOLSET_Convert_To_Mask.bl_idname)
        layout.operator(MATERIALS_OT_METAV_TOOLSET_Correct_ColorData.bl_idname)
        return None


class MESH_PT_METAV_TOOLSET(bpy.types.Panel):
    """ Panel for Mesh related tools """
    bl_label = "Mesh Tools"

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "High Fidelity"

    @classmethod
    def poll(self, context):
        return len(context.selected_objects) == 1 and context.active_object.type == "MESH"

    def draw(self, context):
        layout = self.layout

        layout.operator(MESH_OT_METAV_TOOL_Merge_Modifiers_Shapekey.bl_idname)
        layout.operator(
            MESH_OT_METAV_TOOL_Clean_Unused_Vertex_Groups.bl_idname)
        return None


class SCENE_PT_METAV_TOOLSET(bpy.types.Panel):
    """ Panel for Scene related tools """
    bl_label = "Scene Tools"

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "High Fidelity"

    def draw(self, context):
        layout = self.layout
        layout.operator(
            SCENE_OT_METAV_TOOLSET_Fix_Scene_Env_Rotation.bl_idname)

        return None


class OBJECT_PT_METAV_TOOLSET_Assets_Display(bpy.types.Panel):
    """ Panel for IPFS-Gateway Asset related access tools """
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
        layout.operator(EXPORT_OT_METAV_TOOLSET_IPFS_Assets_Toolset.bl_idname)
        return None


class OBJECT_PT_METAV_TOOLSET_Assets_Display(bpy.types.Panel):
    """ Panel for IPFS-Gateway Asset related access tools """
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
        layout.operator(EXPORT_OT_METAV_TOOLSET_IPFS_Assets_Toolset.bl_idname)
        return None


class EXPORT_OT_METAV_TOOLSET_IPFS_Assets_Toolset(bpy.types.Operator):
    """ Operator meant to open a browser to the current active ipfs gateway """
    bl_idname = "metaverse_toolset.hf_ipfs_assets_toolset"
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


class ARMATURE_OT_METAV_TOOLSET_Create_Operator(bpy.types.Operator):
    """ Tool to quickly create a Hifi specific Avatar Skeleton """
    bl_idname = "metaverse_toolset.hf_create_armature"
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


class ARMATURE_OT_METAV_TOOLSET_Set_Rest_Pose_Operator(bpy.types.Operator):
    """ Tool to quickly set the skeleton into restpose, and do some quick
        fix operations to the skeleton scale and rotation """
    bl_idname = "metaverse_toolset.set_armature_rest_pose"
    bl_label = "Rest TPose"

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "High Fidelity"

    def execute(self, context):
        bones_builder.retarget_armature({'apply': False}, bpy.data.objects)
        return {'FINISHED'}


class ARMATURE_OT_METAV_TOOLSET_Clear_Rest_Pose_Operator(bpy.types.Operator):
    """ Tool to clear the armature rest pose, allowing one to adjust
        the pose of the armatures """
    bl_idname = "metaverse_toolset.clear_armature_rest_pose"
    bl_label = "Clear Pose"

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "High Fidelity"

    def execute(self, context):
        bones_builder.clear_pose(bpy.data.objects)
        return {'FINISHED'}


class OBJECT_OT_METAV_TOOLSET_Fix_Scale_Operator(bpy.types.Operator):
    """ Tool fix armature, and its children scale and rotations """
    bl_idname = "metaverse_toolset.hf_objects_fix_scale_and_rotation"
    bl_label = "Fix Scale and Rotations"

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "High Fidelity"

    def execute(self, context):
        armature = bones_builder.find_armature_or_armature_parent(bpy.context.selected_objects)
        bones_builder.correct_scale_rotation(armature, True)    
        return {'FINISHED'}


class BONES_OT_METAV_TOOLSET_Pin_Problem_Bones(bpy.types.Operator):
    """ Correct Rolls AND Pins usually problemative bones to match the HF reference skeleton. """
    bl_idname = "metaverse_toolset.hf_pin_problem_bones"
    bl_label = "Pin Problem Bones"

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "High Fidelity"

    def execute(self, context):
        for obj in bpy.data.objects:
            if obj.type == "ARMATURE":
                bones_builder.pin_common_bones(obj, False)

        return {'FINISHED'}


class BONES_OT_METAV_TOOLSET_Fix_Rolls(bpy.types.Operator):
    """ Corrects the Rolls to match the expected rolls of the skeleton bones in HF """
    bl_idname = "metaverse_toolset.hf_fix_bone_rolls"
    bl_label = "Match Reference Rolls"

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "High Fidelity"

    def execute(self, context):
        selected = bpy.context.selected_objects
        
        if selected is None:
            selected = bpy.data.objects
        
        bones_builder.find_select_armature_and_children(selected)
        
        selected = bpy.context.selected_objects


        bpy.ops.object.mode_set(mode="EDIT")

        if selected is None:
            selected = bpy.data.objects

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


# Remove once fst export is available
class BONES_OT_METAV_TOOLSET_Set_Physical(bpy.types.Operator):
    """ Sets names for the select bones to match the flow bone setup in HF """
    bl_idname = "metaverse_toolset.hf_set_physical_bones"
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


class BONES_OT_METAV_TOOLSET_Remove_Physical(bpy.types.Operator):
    """ Clears names for the select bones from matching the flow bone setup in HF """
    bl_idname = "metaverse_toolset.hf_remove_physical_bones"
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


class BONES_OT_METAV_TOOLSET_Connect_Selected(bpy.types.Operator):
    """ Connect selected bones to their Parent bones """
    bl_idname = "metaverse_toolset.connect_selected_bones"
    bl_label = "Connect Selected "

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "High Fidelity"

    def execute(self, context):
        bones_builder.bone_connection(context.selected_editable_bones, True)
        return {'FINISHED'}


class BONES_OT_METAV_TOOLSET_Disconnect_Selected(bpy.types.Operator):
    """ Disconnect selected bones to their Parent bones """
    bl_idname = "metaverse_toolset.disconnect_selected_bones"
    bl_label = "Disconnect Selected "

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "High Fidelity"

    def execute(self, context):
        bones_builder.bone_connection(context.selected_editable_bones, False)
        return {'FINISHED'}


class BONES_OT_METAV_TOOLSET_Combine_Disconnected(bpy.types.Operator):
    """ Combine Selected Bones and their Vertex Groups, but do NOT connect the resulting bone to parent """
    bl_idname = "metaverse_toolset.combine_detached_bones"
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


class BONES_OT_METAV_TOOLSET_Combine(bpy.types.Operator):
    """ Combine Selected Bones and their Vertex Groups, connecting the resulting bone to parent """
    bl_idname = "metaverse_toolset.combine_bones"
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


class AVATAR_OT_METAV_TOOLSET_Convert_Custom(bpy.types.Operator):
    """ Converter to bind bones from a custom skeleton into a HF specific one. """
    bl_idname = "metaverse_toolset.hf_convert_custom_avatar"
    bl_label = "Custom Avatar"

    bl_icon = "BONES_DATA"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "High Fidelity"

    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # https://b3d.interplanety.org/en/creating-pop-up-panels-with-user-ui-in-blender-add-on/
        bpy.ops.metaverse_toolset.hf_open_custom_avatar_binder(
            'INVOKE_DEFAULT')
        return {'FINISHED'}


class AVATAR_OT_METAV_TOOLSET_Convert_MMD(bpy.types.Operator):
    """ Converter to update an untranslated MMD avatar into a HF specific one. """
    bl_idname = "metaverse_toolset.hf_convert_mmd_avatar"
    bl_label = "MMD Avatar"

    bl_space_type = "VIEW_3D"
    bl_icon = "BONES_DATA"
    bl_region_type = "UI"
    bl_category = "High Fidelity"

    def execute(self, context):
        mmd.convert_mmd_avatar_hifi()
        return {'FINISHED'}


class AVATAR_OT_METAV_TOOLSET_Convert_Mixamo(bpy.types.Operator):
    """ Converter to update an Mixamo avatar into a HF specific one. """
    bl_idname = "metaverse_toolset.convert_mixamo_avatar"
    bl_label = "Mixamo Avatar"

    bl_icon = "BONES_DATA"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "High Fidelity"

    def execute(self, context):
        mixamo.convert_mixamo_avatar_hifi()
        return {'FINISHED'}


class AVATAR_OT_METAV_TOOLSET_Convert_MakeHuman(bpy.types.Operator):
    """ Converter to update an Makehuman avatar into a HF specific one. """
    bl_idname = "metaverse_toolset.convert_makehuman_avatar"
    bl_label = "MakeHuman Avatar"

    bl_icon = "BONES_DATA"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "High Fidelity"

    def execute(self, context):
        makehuman.convert_makehuman_avatar_hifi()
        bones_builder.retarget_armature({'apply': True}, bpy.data.objects)
        return {'FINISHED'}


class TEXTURES_OT_METAV_TOOLSET_Convert_To_Png(bpy.types.Operator):
    """ Converter to update All scene Textures to PNG """
    bl_idname = "metaverse_toolset.hf_convert_textures_to_png"
    bl_label = "Textures to PNG"

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "High Fidelity"

    def execute(self, context):
        materials.convert_to_png(bpy.data.images)
        return {'FINISHED'}


# Probably Depricated soon
class TEXTURES_OT_METAV_TOOLSET_Convert_To_Mask(bpy.types.Operator):
    """ Converter to update All scene Textures to a Masked Texture """
    bl_idname = "metaverse_toolset.hf_convert_textures_to_masked"
    bl_label = "Textures to Masked"

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "High Fidelity"

    def execute(self, context):
        materials.convert_images_to_mask(bpy.data.images)
        return {'FINISHED'}


# -----

class SAVE_OT_METAV_TOOLSET_Message_Remind_Save(bpy.types.Operator):
    """ Message to remind user to save their scene prior to continuing """
    bl_idname = "metaverse_toolset_messages.remind_save"
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


class MATERIALS_OT_METAV_TOOLSET_Correct_ColorData(bpy.types.Operator):
    """ Helper Operator that changes all the Non-color textures Color Data to be correct in Blender. """
    bl_idname = "metaverse_toolset.correct_colordata"
    bl_label = "Set Non-Diffuse ColorData to None"

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "High Fidelity"

    def execute(self, context):
        materials.correct_all_color_spaces_to_non_color(context)
        return {'FINISHED'}


class HELP_OT_METAV_TOOLSET_Open_Forum_Link(bpy.types.Operator):
    """ Helper Operator to open the forum post regarding this plugin """
    bl_idname = "metaverse_toolset.hf_open_forum_link"
    bl_label = "HF Forum Thread / Bug Reports"

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


class MESH_OT_METAV_TOOL_Message_Processing(bpy.types.Operator):
    """ This Operator is used show yes indeed we are doing something.
    """
    bl_idname = "metaverse_toolset_messages.processing"
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
        row.label(text="Notice:", icon="QUESTION")
        row = layout.row()
        row.label(
            text="Processing: This may take a while. Click Out to see when done")


class MESH_OT_METAV_TOOL_Message_Done(bpy.types.Operator):
    """ This Operator is used show we are done
    """
    bl_idname = "metaverse_toolset_messages.done"
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
        row.label(text="Done!", icon="FILE_TICK")


class MESH_OT_METAV_TOOL_Merge_Modifiers_Shapekey(bpy.types.Operator):
    """ Helper Operator to attempt to merge modifiers onto Mesh with Shapekeys using Przemysław Bągard's ApplyModifierForObjectWithShapeKeys modified for 2.8 """
    bl_idname = "metaverse_toolset.merge_modifiers_on_shapekeys"
    bl_label = "Merge Modifiers & Shapekeys"

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "High Fidelity"

    @classmethod
    def poll(self, context):
        return context.active_object.type == "MESH" and len(context.active_object.data.shape_keys.key_blocks) > 0

    def execute(self, context):
        bpy.ops.object.apply_modifier_for_object_with_shape_keys(
            'INVOKE_DEFAULT')

        return {"FINISHED"}


class MESH_OT_METAV_TOOL_Clean_Unused_Vertex_Groups(bpy.types.Operator):
    """ Helper Operator to clean a mesh from unused vertex groups (groups that have not been bound to armature)"""
    bl_idname = "metaverse_toolset.clean_unused_vertex_groups"
    bl_label = "Clean Unused Vertex Groups"

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "High Fidelity"

    @classmethod
    def poll(self, context):
        return context.active_object.type == "MESH" and len(context.active_object.vertex_groups) > 0

    def execute(self, context):
        mesh.clean_unused_vertex_groups(context.active_object)
        return {"FINISHED"}


class BONES_OT_METAV_TOOLSET_Debug_Armature_Operator(bpy.types.Operator):
    bl_idname = "metaverse_toolset.hf_debug_armature"
    bl_label = "debug armature"

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "High Fidelity"

    def execute(self, context):
        armature_debug()
        return {"FINISHED"}


class SCENE_OT_METAV_TOOLSET_Fix_Scene_Env_Rotation(bpy.types.Operator):
    bl_idname = "metaverse_toolset.hf_fix_scene_rotation"
    bl_label = "Match HF Env Rotation"

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "High Fidelity"

    def execute(self, context):
        materials.fix_env_rotations()
        return {"FINISHED"}


classes = (
    AVATAR_PT_METAV_TOOLSET,
    EXPORT_OT_METAV_TOOLSET_IPFS_Assets_Toolset,

    BONES_PT_METAV_TOOLSET,
    ARMATURE_OT_METAV_TOOLSET_Create_Operator,
    ARMATURE_OT_METAV_TOOLSET_Set_Rest_Pose_Operator,
    ARMATURE_OT_METAV_TOOLSET_Clear_Rest_Pose_Operator,

    BONES_OT_METAV_TOOLSET_Set_Physical,
    BONES_OT_METAV_TOOLSET_Remove_Physical,
    BONES_OT_METAV_TOOLSET_Combine,
    BONES_OT_METAV_TOOLSET_Combine_Disconnected,
    BONES_OT_METAV_TOOLSET_Connect_Selected,
    BONES_OT_METAV_TOOLSET_Fix_Rolls,
    BONES_OT_METAV_TOOLSET_Disconnect_Selected,
    BONES_OT_METAV_TOOLSET_Pin_Problem_Bones,
    OBJECT_PT_METAV_TOOLSET,
    OBJECT_PT_METAV_TOOLSET_Assets_Display,

    AVATAR_OT_METAV_TOOLSET_Convert_Custom,
    # AVATAR_OT_METAV_TOOLSET_Convert_MakeHuman,
    AVATAR_OT_METAV_TOOLSET_Convert_MMD,
    # AVATAR_OT_METAV_TOOLSET_Convert_Mixamo,

    MATERIALS_PT_METAV_TOOLSET,
    MATERIALS_OT_METAV_TOOLSET_Correct_ColorData,
    TEXTURES_OT_METAV_TOOLSET_Convert_To_Png,
    TEXTURES_OT_METAV_TOOLSET_Convert_To_Mask,

    OBJECT_OT_METAV_TOOLSET_Fix_Scale_Operator,
    SAVE_OT_METAV_TOOLSET_Message_Remind_Save,
    HELP_OT_METAV_TOOLSET_Open_Forum_Link,
    # DebugArmatureOperator,

    MESH_PT_METAV_TOOLSET,
    MESH_OT_METAV_TOOL_Message_Done,
    MESH_OT_METAV_TOOL_Message_Processing,
    MESH_OT_METAV_TOOL_Merge_Modifiers_Shapekey,
    MESH_OT_METAV_TOOL_Clean_Unused_Vertex_Groups,

    SCENE_PT_METAV_TOOLSET,
    SCENE_OT_METAV_TOOLSET_Fix_Scene_Env_Rotation
)


module_register, module_unregister = bpy.utils.register_classes_factory(
    classes)


def armature_create_menu_func(self, context):
    self.layout.operator("ARMATURE_OT_METAV_TOOLSET_Create_Operator",
                         text="Add HiFi Armature",
                         icon="BONES_DATA")


def register():
    module_register()


def unregister():
    module_unregister()
