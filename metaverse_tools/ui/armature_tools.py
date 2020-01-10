import bpy
from metaverse_tools.utils.bones import bones_builder, mmd, mixamo, makehuman
from metaverse_tools.armature import SkeletonTypes


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
        layout.operator(BONES_OT_MVT_TOOLSET_Rename_Chain.bl_idname)
        layout.operator(BONES_OT_MVT_TOOLSET_Remove_001.bl_idname)
        layout.operator(BONES_OT_MVT_TOOLSET_Mirror_And_Rename_On_X.bl_idname)
        return None


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
                {'apply': False}, bpy.context.view_layer.objects, skeleton)
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
        bones_builder.clear_pose(bpy.context.view_layer.objects)
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

class BONES_OT_MVT_TOOLSET_Rename_Chain(bpy.types.Operator):
    """ Rename bones to Chain From Root Name and Numbers Accordingly """
    bl_idname = "metaverse_toolset.rename_bone_chain"
    bl_label = "Rename Chain to Root"

    bl_region_type = "TOOLS"
    bl_space_type = "VIEW_3D"

    @classmethod
    def poll(self, context):
        return context.selected_bones is not None and len(context.selected_bones) > 1

    def execute(self, context):
        name = context.selected_bones[0].name
        bones_builder.rename_selected_bone_chain(name, context.selected_bones)
        return {'FINISHED'}


class BONES_OT_MVT_TOOLSET_Remove_001(bpy.types.Operator):
    """ Remove .001 endings """
    bl_idname = "metaverse_toolset.remove_bone_001_ending"
    bl_label = "Remove .001 from Names"

    bl_region_type = "TOOLS"
    bl_space_type = "VIEW_3D"

    @classmethod
    def poll(self, context):
        return context.selected_bones is not None and len(context.selected_bones) > 1

    def execute(self, context):
        bones_builder.remove_001_endings(context.selected_bones)
        return {'FINISHED'}



class BONES_OT_MVT_TOOLSET_Mirror_And_Rename_On_X(bpy.types.Operator):
    """ Mirrors and renames selected on the X axis """
    bl_idname = "metaverse_toolset.bones_mirror_and_rename"
    bl_label = "Mirror Bones"

    bl_region_type = "TOOLS"
    bl_space_type = "VIEW_3D"

    @classmethod
    def poll(self, context):
        return context.selected_bones is not None and len(context.selected_bones) > 0

    def execute(self, context):
        bones_builder.mirror_bones_x_and_rename()
        return {'FINISHED'}



classes = (
    BONES_PT_MVT_TOOLSET,
    ARMATURE_OT_MVT_TOOLSET_Force_Pose_Operator,
    ARMATURE_OT_MVT_TOOLSET_Clear_Rest_Pose_Operator,
    BONES_OT_MVT_TOOLSET_Combine,
    BONES_OT_MVT_TOOLSET_Combine_Disconnected,
    BONES_OT_MVT_TOOLSET_Connect_Selected,
    BONES_OT_MVT_TOOLSET_Disconnect_Selected,
    BONES_OT_MVT_TOOLSET_Rename_Chain,
    BONES_OT_MVT_TOOLSET_Remove_001,
    BONES_OT_MVT_TOOLSET_Mirror_And_Rename_On_X,
    ARMATURE_PT_MVT_TOOLSET,
    OBJECT_OT_MVT_TOOLSET_Fix_Scale_Operator
)


module_register, module_unregister = bpy.utils.register_classes_factory(
    classes)


def register_operators():
    module_register()


def unregister_operators():
    module_unregister()
