
import bpy

def set_optional_area_context_type(target_mode):
    area_type = bpy.context.area.type

    # If this is triggered above, then
    if area_type == "":
        return

    bpy.context.area.type = target_mode