import bpy

category = "MVT: Generic Tools"



class AVATAR_PT_MVT_metaverse_toolset_generic(bpy.types.Panel):
    """ Panel for Avatar related conversion tools """
    bl_label = "Avatar Tools"
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
            AVATAR_OT_MVT_TOOLSET_Convert_Custom_To.bl_idname, icon="OUTLINER_OB_ARMATURE")

        return None


class AVATAR_OT_MVT_TOOLSET_Convert_Custom_To(bpy.types.Operator):
    """ Converter to bind bones from a custom skeleton to own  one. """
    bl_idname = "metaverse_toolset.convert_custom_avatar"
    bl_label = "Custom Avatar"

    bl_icon = "BONES_DATA"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = category

    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # https://b3d.interplanety.org/en/creating-pop-up-panels-with-user-ui-in-blender-add-on/
        bpy.ops.metaverse_toolset.open_custom_avatar_binder(
            'INVOKE_DEFAULT')
        return {'FINISHED'}



classes = (
    AVATAR_PT_MVT_metaverse_toolset_generic,
    AVATAR_OT_MVT_TOOLSET_Convert_Custom_To,
)


module_register, module_unregister = bpy.utils.register_classes_factory(
    classes)

