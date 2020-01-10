import bpy
from metaverse_tools.utils.helpers import materials

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


class MATERIALS_OT_MVT_TOOLSET_Correct_ColorData(bpy.types.Operator):
    """ Helper Operator that changes all the Non-color textures Color Data to be correct in Blender. """
    bl_idname = "metaverse_toolset.correct_colordata"
    bl_label = "Set Non-Diffuse ColorData to None"

    bl_region_type = "TOOLS"
    bl_space_type = "VIEW_3D"

    def execute(self, context):
        materials.correct_all_color_spaces_to_non_color(context)
        return {'FINISHED'}


classes = (
    MATERIALS_PT_MVT_TOOLSET,
    MATERIALS_OT_MVT_TOOLSET_Correct_ColorData,
    TEXTURES_OT_MVT_TOOLSET_Convert_To_Png,
    TEXTURES_OT_MVT_TOOLSET_Convert_To_Mask
)


module_register, module_unregister = bpy.utils.register_classes_factory(classes)


def register_operators():
    module_register()


def unregister_operators():
    module_unregister()