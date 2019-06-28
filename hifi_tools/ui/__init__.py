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
from hifi_tools.armature import SkeletonTypes
from . import hifi as hifi_ui
from . import vrc as vrc_ui

category = "MVT: General Tools"


class ARMATURE_PT_MVT_TOOLSET(bpy.types.Panel):
    """ Panel for Object related tools """
    bl_label = "Armature Tools"
    bl_icon = "OBJECT_DATA"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"

    @classmethod
    def poll(self, context):
        return (context.mode == "OBJECT" or context.mode == "POSE") and (context.active_object is not None and context.active_object.type == "ARMATURE")

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.operator(
            ARMATURE_OT_MVT_TOOLSET_Force_Pose_Operator.bl_idname, icon='OUTLINER_OB_ARMATURE',
            emboss=False)
        row.operator(
            ARMATURE_OT_MVT_TOOLSET_Clear_Rest_Pose_Operator.bl_idname, icon='ARMATURE_DATA',
            emboss=False)

        layout.operator(
            OBJECT_OT_MVT_TOOLSET_Fix_Scale_Operator.bl_idname, icon='EMPTY_ARROWS', emboss=False)
        # layout.operator(HifiDebugArmatureOperator.bl_idname)
        # layout.operator(HifiArmatureRetargetPoseOperator.bl_idname)
        return None


class BONES_PT_MVT_TOOLSET(bpy.types.Panel):
    """ Panel for Bone related tools """
    bl_label = "General Bones Tools"

    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"

    @classmethod
    def poll(self, context):
        return context.mode == "EDIT_ARMATURE"

    def draw(self, context):
        layout = self.layout
        # layout.operator(BONES_OT_MVT_TOOLSET_Set_Physical.bl_idname)
        # layout.operator(BONES_OT_MVT_TOOLSET_Remove_Physical.bl_idname)

        layout.operator(BONES_OT_MVT_TOOLSET_Combine.bl_idname)
        layout.operator(BONES_OT_MVT_TOOLSET_Combine_Disconnected.bl_idname)
        layout.operator(BONES_OT_MVT_TOOLSET_Connect_Selected.bl_idname)
        layout.operator(BONES_OT_MVT_TOOLSET_Disconnect_Selected.bl_idname)
        return None


class MATERIALS_PT_MVT_TOOLSET(bpy.types.Panel):
    """ Panel for Material related tools """
    bl_label = "Material Tools"
    bl_region_type = "TOOLS"
    bl_space_type = "VIEW_3D"

    @classmethod
    def poll(self, context):
        return context.mode == "OBJECT"

    def draw(self, context):
        layout = self.layout

        layout.operator(
            TEXTURES_OT_MVT_TOOLSET_Convert_To_Png.bl_idname, icon='TEXTURE', emboss=False)
        layout.operator(
            TEXTURES_OT_MVT_TOOLSET_Convert_To_Mask.bl_idname,  icon='NODE_TEXTURE', emboss=False)
        layout.operator(
            MATERIALS_OT_MVT_TOOLSET_Correct_ColorData.bl_idname, icon='COLORSET_10_VEC', emboss=False)
        return None


class MESH_PT_MVT_TOOLSET(bpy.types.Panel):
    """ Panel for Mesh related tools """
    bl_label = "Mesh Tools"

    bl_region_type = "TOOLS"
    bl_space_type = "VIEW_3D"

    @classmethod
    def poll(self, context):
        return len(context.selected_objects) == 1 and context.active_object.type == "MESH"

    def draw(self, context):
        layout = self.layout

        layout.operator(
            MESH_OT_MVT_TOOL_Merge_Modifiers_Shapekey.bl_idname, icon='MODIFIER_DATA',  emboss=False)
        layout.operator(
            MESH_OT_MVT_TOOL_Clean_Unused_Vertex_Groups.bl_idname, icon='NORMALS_VERTEX',  emboss=False)
        return None


class OBJECT_PT_MVT_TOOLSET_Assets_Display(bpy.types.Panel):
    """ Panel for IPFS-Gateway Asset related access tools """
    bl_label = "Assets"
    bl_region_type = "TOOLS"

    bl_space_type = "VIEW_3D"

    @classmethod
    def poll(self, context):
        user_preferences = context.preferences
        addon_prefs = user_preferences.addons[hifi_tools.__name__].preferences
        return "gateway_token" in addon_prefs and len(addon_prefs["gateway_token"]) > 0

    def draw(self, context):
        layout = self.layout
        layout.operator(
            EXPORT_OT_MVT_TOOLSET_IPFS_Assets_Toolset.bl_idname, emboss=False)
        return None


class EXPORT_OT_MVT_TOOLSET_IPFS_Assets_Toolset(bpy.types.Operator):
    """ Operator meant to open a browser to the current active ipfs gateway """
    bl_idname = "metaverse_toolset.hf_ipfs_assets_toolset"
    bl_label = "IPFS Uploads"

    bl_region_type = "TOOLS"
    bl_space_type = "VIEW_3D"

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


# Remove once fst export is available


class ARMATURE_OT_MVT_TOOLSET_Force_Pose_Operator(bpy.types.Operator):
    """ Tool to quickly set the skeleton into restpose, and do some quick
        fix operations to the skeleton scale and rotation """
    bl_idname = "metaverse_toolset.set_armature_rest_pose"
    bl_label = "Force TPose"

    bl_region_type = "TOOLS"
    bl_space_type = "VIEW_3D"

    def execute(self, context):
        skeleton = SkeletonTypes.get_type_from_armature(context.active_object)
        if skeleton is not None:
            bones_builder.retarget_armature(
                {'apply': False}, bpy.data.objects, skeleton)
        else:
            print("Could not get find Skeleton type of " +
                  context.active_object.name)

        return {'FINISHED'}


class ARMATURE_OT_MVT_TOOLSET_Clear_Rest_Pose_Operator(bpy.types.Operator):
    """ Tool to clear the armature rest pose, allowing one to adjust
        the pose of the armatures """
    bl_idname = "metaverse_toolset.clear_armature_rest_pose"
    bl_label = "Clear Pose"
    bl_region_type = "TOOLS"

    bl_space_type = "VIEW_3D"

    def execute(self, context):
        bones_builder.clear_pose(bpy.data.objects)
        return {'FINISHED'}


class OBJECT_OT_MVT_TOOLSET_Fix_Scale_Operator(bpy.types.Operator):
    """ Tool fix armature, and its children scale and rotations """
    bl_idname = "metaverse_toolset.objects_fix_scale_and_rotation"
    bl_label = "Fix Scale and Rotations"
    bl_region_type = "TOOLS"

    bl_space_type = "VIEW_3D"

    def execute(self, context):
        armature = bones_builder.find_armature_or_armature_parent(
            bpy.context.selected_objects)
        bones_builder.correct_scale_rotation(armature, True)
        return {'FINISHED'}


class BONES_OT_MVT_TOOLSET_Connect_Selected(bpy.types.Operator):
    """ Connect selected bones to their Parent bones """
    bl_idname = "metaverse_toolset.connect_selected_bones"
    bl_label = "Connect Selected "
    bl_region_type = "TOOLS"

    bl_space_type = "VIEW_3D"

    def execute(self, context):
        bones_builder.bone_connection(context.selected_editable_bones, True)
        return {'FINISHED'}


class BONES_OT_MVT_TOOLSET_Disconnect_Selected(bpy.types.Operator):
    """ Disconnect selected bones to their Parent bones """
    bl_idname = "metaverse_toolset.disconnect_selected_bones"
    bl_label = "Disconnect Selected "

    bl_region_type = "TOOLS"
    bl_space_type = "VIEW_3D"

    def execute(self, context):
        bones_builder.bone_connection(context.selected_editable_bones, False)
        return {'FINISHED'}


class BONES_OT_MVT_TOOLSET_Combine_Disconnected(bpy.types.Operator):
    """ Combine Selected Bones and their Vertex Groups, but do NOT connect the resulting bone to parent """
    bl_idname = "metaverse_toolset.combine_detached_bones"
    bl_label = "Combine Bones Detached"

    bl_region_type = "TOOLS"
    bl_space_type = "VIEW_3D"

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


class BONES_OT_MVT_TOOLSET_Combine(bpy.types.Operator):
    """ Combine Selected Bones and their Vertex Groups, connecting the resulting bone to parent """
    bl_idname = "metaverse_toolset.combine_bones"
    bl_label = "Combine Bones"

    bl_region_type = "TOOLS"
    bl_space_type = "VIEW_3D"

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


class TEXTURES_OT_MVT_TOOLSET_Convert_To_Png(bpy.types.Operator):
    """ Converter to update All scene Textures to PNG """
    bl_idname = "metaverse_toolset.hf_convert_textures_to_png"
    bl_label = "Textures to PNG"

    bl_region_type = "TOOLS"
    bl_space_type = "VIEW_3D"

    def execute(self, context):
        materials.convert_to_png(bpy.data.images)
        return {'FINISHED'}


# Probably Depricated soon
class TEXTURES_OT_MVT_TOOLSET_Convert_To_Mask(bpy.types.Operator):
    """ Converter to update All scene Textures to a Masked Texture """
    bl_idname = "metaverse_toolset.hf_convert_textures_to_masked"
    bl_label = "Textures to Masked"

    bl_region_type = "TOOLS"
    bl_space_type = "VIEW_3D"

    def execute(self, context):
        materials.convert_images_to_mask(bpy.data.images)
        return {'FINISHED'}


# -----

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


class MATERIALS_OT_MVT_TOOLSET_Correct_ColorData(bpy.types.Operator):
    """ Helper Operator that changes all the Non-color textures Color Data to be correct in Blender. """
    bl_idname = "metaverse_toolset.correct_colordata"
    bl_label = "Set Non-Diffuse ColorData to None"

    bl_region_type = "TOOLS"
    bl_space_type = "VIEW_3D"

    def execute(self, context):
        materials.correct_all_color_spaces_to_non_color(context)
        return {'FINISHED'}


class MESH_OT_MVT_TOOL_Message_Processing(bpy.types.Operator):
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


class MESH_OT_MVT_TOOL_Message_Done(bpy.types.Operator):
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


class MESH_OT_MVT_TOOL_Merge_Modifiers_Shapekey(bpy.types.Operator):
    """ Helper Operator to attempt to merge modifiers onto Mesh with Shapekeys using Przemysław Bągard's ApplyModifierForObjectWithShapeKeys modified for 2.8 """
    bl_idname = "metaverse_toolset.merge_modifiers_on_shapekeys"
    bl_label = "Merge Modifiers & Shapekeys"

    bl_space_type = "VIEW_3D"

    @classmethod
    def poll(self, context):
        return context.active_object.type == "MESH" and context.active_object.data.shape_keys is not None and len(context.active_object.data.shape_keys.key_blocks) > 0

    def execute(self, context):
        bpy.ops.object.apply_modifier_for_object_with_shape_keys(
            'INVOKE_DEFAULT')

        return {"FINISHED"}


class MESH_OT_MVT_TOOL_Clean_Unused_Vertex_Groups(bpy.types.Operator):
    """ Helper Operator to clean a mesh from unused vertex groups (groups that have not been bound to armature)"""
    bl_idname = "metaverse_toolset.clean_unused_vertex_groups"
    bl_label = "Clean Unused Vertex Groups"

    bl_space_type = "VIEW_3D"

    @classmethod
    def poll(self, context):
        return context.active_object.type == "MESH" and len(context.active_object.vertex_groups) > 0

    def execute(self, context):
        mesh.clean_unused_vertex_groups(context.active_object)
        return {"FINISHED"}


"""
class BONES_OT_MVT_TOOLSET_Debug_Armature_Operator(bpy.types.Operator):
    bl_idname = "metaverse_toolset.hf_debug_armature"
    bl_label = "debug armature"

    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    

    def execute(self, context):
        armature_debug()
        return {"FINISHED"}
s"""


class TEST_WT_workspace(bpy.types.WorkSpaceTool):
    bl_space_type = "VIEW_3D"
    bl_context_mode = "OBJECT"
    bl_idname = "metaverse_toolset.test"
    bl_label = "Boop"
    bl_category = "New Stuff"
    bl_description = (
        "This is\n"
        "A TeSt"
    )
    bl_icon = "ops.generic.select_circle"


classes = (

    BONES_PT_MVT_TOOLSET,
    ARMATURE_OT_MVT_TOOLSET_Force_Pose_Operator,
    ARMATURE_OT_MVT_TOOLSET_Clear_Rest_Pose_Operator,

    BONES_OT_MVT_TOOLSET_Combine,
    BONES_OT_MVT_TOOLSET_Combine_Disconnected,
    BONES_OT_MVT_TOOLSET_Connect_Selected,
    BONES_OT_MVT_TOOLSET_Disconnect_Selected,
    ARMATURE_PT_MVT_TOOLSET,
    OBJECT_PT_MVT_TOOLSET_Assets_Display,

    EXPORT_OT_MVT_TOOLSET_IPFS_Assets_Toolset,

    # AVATAR_PT_MVT_TOOLSET,
    # BONES_OT_MVT_TOOLSET_Fix_Rolls,
    # BONES_OT_MVT_TOOLSET_Pin_Problem_Bones,
    # AVATAR_OT_MVT_TOOLSET_Convert_Custom,
    # AVATAR_OT_MVT_TOOLSET_Convert_MakeHuman,
    # AVATAR_OT_MVT_TOOLSET_Convert_MMD,
    # AVATAR_OT_MVT_TOOLSET_Convert_Mixamo,

    MATERIALS_PT_MVT_TOOLSET,
    MATERIALS_OT_MVT_TOOLSET_Correct_ColorData,
    TEXTURES_OT_MVT_TOOLSET_Convert_To_Png,
    TEXTURES_OT_MVT_TOOLSET_Convert_To_Mask,

    OBJECT_OT_MVT_TOOLSET_Fix_Scale_Operator,
    SAVE_OT_MVT_TOOLSET_Message_Remind_Save,
    # HELP_OT_MVT_TOOLSET_Open_Forum_Link,
    # DebugArmatureOperator,

    MESH_PT_MVT_TOOLSET,
    MESH_OT_MVT_TOOL_Message_Done,
    MESH_OT_MVT_TOOL_Message_Processing,
    MESH_OT_MVT_TOOL_Merge_Modifiers_Shapekey,
    MESH_OT_MVT_TOOL_Clean_Unused_Vertex_Groups,

)


module_register, module_unregister = bpy.utils.register_classes_factory(
    classes)


def register_operators():
    module_register()
    hifi_ui.module_register()
    vrc_ui.module_register()

    # bpy.utils.register_tool(TEST_WT_workspace)


def unregister_operators():
    module_unregister()
    hifi_ui.module_unregister()
    vrc_ui.module_unregister()
    # bpy.utils.unregister_tool(TEST_WT_workspace)
