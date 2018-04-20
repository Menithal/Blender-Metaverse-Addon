
import bpy


def make_materials_shadeless(materials_slots):
    for material_slot in materials_slots:
        print(material_slot)
        material = material_slot.material
        material.specular_shader = 'WARDISO'
        material.use_shadeless = True
        material.specular_color = (0, 0, 0)


# Returns all textures that match the texture_type
def get_textures_for_slot(texture_slots, texture_type="ALL"):
    texture_list = []

    for slot in texture_slots:
        if slot.image is not None and (texture_type == "ALL" or
                                       (texture_type == "COLOR" and slot.use_map_color_diffuse) or
                                       (texture_type == "SPECULAR" and (slot.use_map_color_spec or slot.use_map_specular)) or
                                       (texture_type == "NORMAL" and slot.use_map_normal) or
                                       (texture_type == "ALPHA" and slot.use_map_alpha) or
                                       (texture_type == "EMIT" and slot.use_map_emit) or
                                       (texture_type == "EMISSION" and slot.use_map_emission) or
                                       (texture_type == "HARDNESS" and slot.use_map_hardness) or
                                       (texture_type == "ROUGHNESS" and slot.use_map_roughness)) and slot.image not in texture_list:

            texture_list.append(slot.image)

    return texture_list


def merge_textures(materials_slots, unique_textures=None):
    if unique_textures is None:
        unique_textures = {}
        for slot in materials_slots:
            textures = get_textures_for_slot(slot.texture_slots)
            if len ( textures) > 0:
                unique_textures[textures[0].name] = textures

    for key in unique_textures.keys():
        material_list = unique_textures[key]

        if material_list is None:
            continue

        print("Creating new material Texture", key)
        n = material_list.pop(0)
        first_material = materials_slots.get(n)
        if first_material is None:
            print("Could not find", first_material)
            continue
        root_material = key + "_material"
        first_material.material.name = root_material
        root_index = materials_slots.find(root_material)

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        if len(material_list) > 0:

            for material in material_list:
                index = materials_slots.find(material)
                if index > -1:
                    print("  + Selecting", key, material)
                    bpy.context.object.active_material_index = index
                    bpy.ops.object.material_slot_select()

        print("  + Selecting", key)
        bpy.context.object.active_material_index = root_index
        bpy.ops.object.material_slot_select()

        print(" + Assigning to", key)
        bpy.ops.object.material_slot_assign()

        bpy.ops.object.mode_set(mode='OBJECT')
        print(" - Clean up", key)
        if len(material_list) > 0:
            for material in material_list:
                index = materials_slots.find(material)

                if index > -1:
                    print("  - Deleting", material)
                    bpy.context.object.active_material_index = index
                    bpy.ops.object.material_slot_remove()
