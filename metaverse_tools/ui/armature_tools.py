import bpy
from metaverse_tools.utils.bones import bones_builder, mmd, mixamo, makehuman
from metaverse_tools.armature import SkeletonTypes




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

        layout.operator(BONES_OT_MVT_TOOLSET_Reparent_To_Last.bl_idname)

        layout.operator(BONES_OT_MVT_TOOLSET_Add_Deform.bl_idname)
        layout.operator(BONES_OT_MVT_TOOLSET_Remove_Deform.bl_idname)
        return None





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



# Depricated, Symmetrize exists
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


class BONES_OT_MVT_TOOLSET_Reparent_To_Last(bpy.types.Operator):
    """ Reparent selected to Last """
    bl_idname = 'metaverse_toolset.bones_reparent_to_last'
    bl_label = 'Reparent to Last'
    bl_region_type = "TOOLS"
    bl_space_types = "VIEW_3D"

    @classmethod
    def poll(self, context):
        return context.selected_bones is not None and len(context.selected_bones) > 1

    def execute(self, context):
        first_name = context.selected_bones[0].name
        bones_builder.reparent_to_parent(first_name, context.selected_bones[1:])

        return {'FINISHED'}

class BONES_OT_MVT_TOOLSET_Remove_Deform(bpy.types.Operator):
    """  """
    bl_idname = 'metaverse_toolset.remove_deform'
    bl_label = 'Remove Deform Flag'
    bl_region_type = "TOOLS"
    bl_space_types = "VIEW_3D"

    @classmethod
    def poll(self, context):
        return context.selected_bones is not None and len(context.selected_bones) > 0

    def execute(self, context):
        bones_builder.set_deform(context.selected_bones, False)
        return {'FINISHED'}

class BONES_OT_MVT_TOOLSET_Add_Deform(bpy.types.Operator):
    """  """
    bl_idname = 'metaverse_toolset.add_deform'
    bl_label = 'Add Deform Flag'
    bl_region_type = "TOOLS"
    bl_space_types = "VIEW_3D"

    @classmethod
    def poll(self, context):
        return context.selected_bones is not None and len(context.selected_bones) > 0

    def execute(self, context):
        bones_builder.set_deform(context.selected_bones, True)
        return {'FINISHED'}




classes = (
    BONES_PT_MVT_TOOLSET,
    BONES_OT_MVT_TOOLSET_Combine,
    BONES_OT_MVT_TOOLSET_Combine_Disconnected,
    BONES_OT_MVT_TOOLSET_Connect_Selected,
    BONES_OT_MVT_TOOLSET_Disconnect_Selected,
    BONES_OT_MVT_TOOLSET_Rename_Chain,
    BONES_OT_MVT_TOOLSET_Remove_001,
    BONES_OT_MVT_TOOLSET_Mirror_And_Rename_On_X,
    BONES_OT_MVT_TOOLSET_Reparent_To_Last,
    BONES_OT_MVT_TOOLSET_Remove_Deform,
    BONES_OT_MVT_TOOLSET_Add_Deform
)


module_register, module_unregister = bpy.utils.register_classes_factory(
    classes)


def register_operators():
    module_register()


def unregister_operators():
    module_unregister()
