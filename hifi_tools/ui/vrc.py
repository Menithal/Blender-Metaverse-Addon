import bpy

from hifi_tools.utils.bones import bones_builder, mmd, mixamo, makehuman
from hifi_tools.armature import SkeletonTypes

category = "MVT: VRC Tools"


class AVATAR_PT_MVT_VRC_TOOLSET(bpy.types.Panel):
    """ Panel for HF Avatar related conversion tools """
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
         
        layout.operator(ARMATURE_OT_MVT_TOOLSET_Create_VRC_Operator.bl_idname)
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


classes = (
    AVATAR_PT_MVT_VRC_TOOLSET,
    ARMATURE_OT_MVT_TOOLSET_Create_VRC_Operator
)

module_register, module_unregister = bpy.utils.register_classes_factory(
    classes)
