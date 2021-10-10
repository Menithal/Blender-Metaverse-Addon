import bpy
from metaverse_tools.utils.bones import bones_builder, pose_helper
from metaverse_tools.armature import SkeletonTypes


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

class ARMATURE_PT_MVT_BONE_UTILITY(bpy.types.Panel):
    """ Panel for Pose related tools """
    bl_label = "Pose Utility Tools"
    bl_icon = "OBJECT_DATA"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"

    @classmethod
    def poll(self, context):
        return (context.mode == "OBJECT" or context.mode == "POSE") and (context.active_object is not None and context.active_object.type == "ARMATURE")

    def draw(self, context):
        layout = self.layout

        
        layout.operator(
            ARMATURE_OT_MVT_TOOLSET_Clone_Locks.bl_idname)
        
        row = layout.row()
            
        row.operator(
            ARMATURE_OT_MVT_TOOLSET_Lock_Rotations.bl_idname)
        row.operator(
            ARMATURE_OT_MVT_TOOLSET_Unlock_Rotations.bl_idname)
        row = layout.row()
            
        row.operator(
            ARMATURE_OT_MVT_TOOLSET_Lock_Translations.bl_idname)
        row.operator(
            ARMATURE_OT_MVT_TOOLSET_Unlock_Translations.bl_idname)
            
        layout.operator(
            ARMATURE_OT_MVT_TOOLSET_Copy_Custom_Shapes.bl_idname)
            
        layout.operator(
            ARMATURE_OT_MVT_TOOLSET_Clear_Custom_Shapes.bl_idname)

    
class ARMATURE_PT_MVT_POSE_TOOLSET(bpy.types.Panel):
    """ Panel for Pose related tools """
    bl_label = "Pose Constraint Tools"
    bl_icon = "OBJECT_DATA"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"

    @classmethod
    def poll(self, context):
        return (context.mode == "OBJECT" or context.mode == "POSE") and (context.active_object is not None and context.active_object.type == "ARMATURE")

    def draw(self, context):
        layout = self.layout


        layout.operator(
            ARMATURE_OT_MVT_TOOLSET_Clear_Constraint.bl_idname)
            
        row = layout.row()
        row.operator(
            ARMATURE_OT_MVT_TOOLSET_Add_Location_Constraint.bl_idname)
        row.operator(
            ARMATURE_OT_MVT_TOOLSET_Add_Influenced_Location_Constraint.bl_idname)
            
        layout.operator(
            ARMATURE_OT_MVT_TOOLSET_Add_Copy_Rotational_Constraint.bl_idname)

        layout.operator(
            ARMATURE_OT_MVT_TOOLSET_Mirror_Constraints.bl_idname)


        
        layout.operator(
            ARMATURE_OT_MVT_TOOLSET_Copy_Limits.bl_idname)

            
    #    layout.operator(
    #        ARMATURE_OT_MVT_TOOLSET_Normalize_Influences.bl_idname)
        return None



class ARMATURE_OT_MVT_TOOLSET_Clear_Constraint(bpy.types.Operator):
    """ Removes all Constraints from bones """
    bl_idname = "metaverse_toolset.armature_clear_constraint"
    bl_label = "Clear Constraints"
    bl_region_type = "TOOLS"

    bl_space_type = "VIEW_3D"

    @classmethod
    def poll(self, context):
        return context.selected_pose_bones is not None and len(context.selected_pose_bones) >= 1

    def execute(self, context):
        pose_helper.purge_constraints(context.selected_pose_bones)
        return {'FINISHED'}


class ARMATURE_OT_MVT_TOOLSET_Add_Location_Constraint(bpy.types.Operator):
    """  """
    bl_idname = "metaverse_toolset.pose_location_copy_constraints"
    bl_label = "Location Copy"
    bl_region_type = "TOOLS"

    bl_space_type = "VIEW_3D"
    @classmethod
    def poll(self, context):
        return context.selected_pose_bones is not None and len(context.selected_pose_bones) > 1

    def execute(self, context):
        pose_helper.add_local_pose_constraint_bone(context.active_object, 
            context.selected_pose_bones[:-1],
            context.active_pose_bone,
            "COPY_LOCATION",
            False)
        return {'FINISHED'}


class ARMATURE_OT_MVT_TOOLSET_Add_Copy_Rotational_Constraint(bpy.types.Operator):
    """  Adds COPY Rotation constraint from active bone to selected bones """
    bl_idname = "metaverse_toolset.pose_rotation_copy_constraints"
    bl_label = "Rotational Copy"
    bl_region_type = "TOOLS"

    bl_space_type = "VIEW_3D"
    @classmethod
    def poll(self, context):
        return context.selected_pose_bones is not None and len(context.selected_pose_bones) > 1

    def execute(self, context):
        pose_helper.add_local_pose_constraint_bone(context.active_object, 
            context.selected_pose_bones[:-1],
            context.active_pose_bone,
            "COPY_ROTATION",
            False)
        return {'FINISHED'}


class ARMATURE_OT_MVT_TOOLSET_Add_Influenced_Location_Constraint(bpy.types.Operator):
    """  """
    bl_idname = "metaverse_toolset.pose_influenced_location_copy_constraints"
    bl_label = "Influenced Copy Location "
    bl_region_type = "TOOLS"

    bl_space_type = "VIEW_3D"
    @classmethod
    def poll(self, context):
        return context.selected_pose_bones is not None and len(context.selected_pose_bones) > 1

    def execute(self, context):
        pose_helper.add_local_pose_constraint_bone(context.active_object, 
            context.selected_pose_bones[:-1],
            context.active_pose_bone,
            "COPY_LOCATION",
            True)
        return {'FINISHED'}

    
class ARMATURE_OT_MVT_TOOLSET_Mirror_Constraints(bpy.types.Operator):
    """ Mirrors all constraints to selected bones from the last selected to ones selected before """
    bl_idname = "metaverse_toolset.mirror_constraints"
    bl_label = "Mirror Constraints"
    bl_region_type = "TOOLS"

    bl_space_type = "VIEW_3D"
    @classmethod
    def poll(self, context):
        return context.selected_pose_bones is not None and len(context.selected_pose_bones) >= 1

    def execute(self, context):
        pose_helper.mirror_pose_constraints(context.active_object, context.selected_pose_bones)
        return {'FINISHED'}


class ARMATURE_OT_MVT_TOOLSET_Clone_Locks(bpy.types.Operator):
    """  """
    bl_idname = "metaverse_toolset.clone_pose_locks"
    bl_label = "Clone Locks"
    bl_region_type = "TOOLS"

    bl_space_type = "VIEW_3D"
    @classmethod
    def poll(self, context):
        return context.selected_pose_bones is not None and len(context.selected_pose_bones) >= 1

    def execute(self, context):
        pose_helper.clone_locks(context.active_pose_bone, context.selected_pose_bones[:-1])
        return {'FINISHED'}


class ARMATURE_OT_MVT_TOOLSET_Lock_Rotations(bpy.types.Operator):
    """  """
    bl_idname = "metaverse_toolset.lock_pose_rotations"
    bl_label = "Lock Rotations"
    bl_region_type = "TOOLS"

    bl_space_type = "VIEW_3D"
    @classmethod
    def poll(self, context):
        return context.selected_pose_bones is not None and len(context.selected_pose_bones) >= 1

    def execute(self, context):
        pose_helper.set_pose_bone_rotation_lock(context.selected_pose_bones, True)
        return {'FINISHED'}


class ARMATURE_OT_MVT_TOOLSET_Unlock_Rotations(bpy.types.Operator):
    """  """
    bl_idname = "metaverse_toolset.unlock_pose_rotations"
    bl_label = "Unlock Rotations"
    bl_region_type = "TOOLS"

    bl_space_type = "VIEW_3D"
    @classmethod
    def poll(self, context):
        return context.selected_pose_bones is not None and len(context.selected_pose_bones) >= 1

    def execute(self, context):
        pose_helper.set_pose_bone_rotation_lock(context.selected_pose_bones, False)
        return {'FINISHED'}


class ARMATURE_OT_MVT_TOOLSET_Lock_Translations(bpy.types.Operator):
    """  """
    bl_idname = "metaverse_toolset.lock_pose_translations"
    bl_label = "Lock Translations"
    bl_region_type = "TOOLS"

    bl_space_type = "VIEW_3D"
    @classmethod
    def poll(self, context):
        return context.selected_pose_bones is not None and len(context.selected_pose_bones) >= 1

    def execute(self, context):
        pose_helper.set_pose_bone_translations_lock(context.selected_pose_bones, True)
        return {'FINISHED'}


class ARMATURE_OT_MVT_TOOLSET_Unlock_Translations(bpy.types.Operator):
    """  """
    bl_idname = "metaverse_toolset.unlock_pose_translations"
    bl_label = "Unlock Translations"
    bl_region_type = "TOOLS"

    bl_space_type = "VIEW_3D"
    @classmethod
    def poll(self, context):
        return context.selected_pose_bones is not None and len(context.selected_pose_bones) >= 1

    def execute(self, context):
        pose_helper.set_pose_bone_translations_lock(context.selected_pose_bones, False)
        return {'FINISHED'}


class ARMATURE_OT_MVT_TOOLSET_Copy_Custom_Shapes(bpy.types.Operator):
    """  """
    bl_idname = "metaverse_toolset.copy_custom_pose_shape"
    bl_label = "Copy Custom Shapes"
    bl_region_type = "TOOLS"

    bl_space_type = "VIEW_3D"
    @classmethod
    def poll(self, context):
        return context.selected_pose_bones is not None and len(context.selected_pose_bones) > 1

    def execute(self, context):
        pose_helper.copy_custom_shape(context.active_pose_bone, context.selected_pose_bones)
        return {'FINISHED'}

        
class ARMATURE_OT_MVT_TOOLSET_Clear_Custom_Shapes(bpy.types.Operator):
    """  """
    bl_idname = "metaverse_toolset.clear_custom_pose_shpae"
    bl_label = "Clear Custom Shapes"
    bl_region_type = "TOOLS"

    bl_space_type = "VIEW_3D"
    @classmethod
    def poll(self, context):
        return context.selected_pose_bones is not None and len(context.selected_pose_bones) >= 1

    def execute(self, context):
        pose_helper.clear_custom_shape(context.selected_pose_bones)
        return {'FINISHED'}



# Add Max Normalization Amount allowing for override?
class ARMATURE_OT_MVT_TOOLSET_Copy_Limits(bpy.types.Operator):
    """  Copies all Constraints that limit the movement of a bone from one to another """
    bl_idname = "metaverse_toolset.copy_pose_constraint_limits"
    bl_label = "Copy Limits"
    bl_region_type = "TOOLS"

    bl_space_type = "VIEW_3D"
    @classmethod
    def poll(self, context):
        return context.selected_pose_bones is not None and len(context.selected_pose_bones) >= 1

    def execute(self, context):
        pose_helper.copy_limit_constraints(context.active_pose_bone, context.selected_pose_bones)
        return {'FINISHED'}

# Add Max Normalization Amount allowing for override?
#class ARMATURE_OT_MVT_TOOLSET_Normalize_Influences(bpy.types.Operator):
#    """ Normalizes influences between any copy location/rotation/ """
#    bl_idname = "metaverse_toolset.normalize_pose_constrain_influences"
#    bl_label = "Normalize Constraint Influences"
#    bl_region_type = "TOOLS"

#    bl_space_type = "VIEW_3D"
#    @classmethod
#    def poll(self, context):
#        return context.selected_pose_bones is not None and len(context.selected_pose_bones) >= 1

#    def execute(self, context):
#        pose_helper.normalize_constraints_rotation(context.selected_pose_bones)
#        return {'FINISHED'}


classes = (
    ARMATURE_PT_MVT_TOOLSET,
    ARMATURE_PT_MVT_POSE_TOOLSET,
    ARMATURE_OT_MVT_TOOLSET_Force_Pose_Operator,
    ARMATURE_OT_MVT_TOOLSET_Clear_Rest_Pose_Operator,
    OBJECT_OT_MVT_TOOLSET_Fix_Scale_Operator,
    ARMATURE_OT_MVT_TOOLSET_Clear_Constraint,
    ARMATURE_OT_MVT_TOOLSET_Add_Location_Constraint,
    ARMATURE_OT_MVT_TOOLSET_Add_Influenced_Location_Constraint,

    ARMATURE_OT_MVT_TOOLSET_Mirror_Constraints,
    ARMATURE_OT_MVT_TOOLSET_Clone_Locks,

    ARMATURE_OT_MVT_TOOLSET_Lock_Rotations,
    ARMATURE_OT_MVT_TOOLSET_Unlock_Rotations,

    ARMATURE_OT_MVT_TOOLSET_Lock_Translations,
    ARMATURE_OT_MVT_TOOLSET_Unlock_Translations,
    ARMATURE_OT_MVT_TOOLSET_Copy_Custom_Shapes,
    ARMATURE_OT_MVT_TOOLSET_Clear_Custom_Shapes,
    #ARMATURE_OT_MVT_TOOLSET_Normalize_Influences,
    ARMATURE_OT_MVT_TOOLSET_Copy_Limits,
    ARMATURE_OT_MVT_TOOLSET_Add_Copy_Rotational_Constraint,
    ARMATURE_PT_MVT_BONE_UTILITY

)


module_register, module_unregister = bpy.utils.register_classes_factory(
    classes)


def register_operators():
    module_register()


def unregister_operators():
    module_unregister()
