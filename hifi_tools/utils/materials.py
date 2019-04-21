# -*- coding: utf-8 -*-
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
# Copyright 2019 Matti 'Menithal' Lahtinen

import copy
import bpy
import re

# TODO: Needs rewrite, as there is an entirely new materials system.

def get_images_from(meshes):
    images = []
    for mesh in meshes:
        if(mesh.type == "MESH"):
            for material_slot in mesh.material_slots:
                print("Iterating material", material_slot)
                if material_slot is not None:
                    material = material_slot.material
                    for node in material.node_tree.nodes:
                        print("Iterating material node", node.name)
                        if node.type == 'TEX_IMAGE' and node.image is not None:
                            images.append(node.image)
    return images



def cleanup_unused(images):
    for image in images:
        pixel_count = len(image.pixels)
        if not (image.users > 0 and pixel_count > 0):
            bpy.data.images.remove(image)


def convert_to_png(images):
    if not bpy.data.is_saved:
        print("Select a Directory")
        bpy.ops.hifi.error_save_file('INVOKE_DEFAULT')
        return

    pack_images(images)
    unpack_images(images)


def pack_images(images):
    mode = bpy.context.area.type
    bpy.context.area.type = 'IMAGE_EDITOR'
    filename_re = re.compile("\\.[a-zA-Z]{2,4}$")
    for image in images:
        pixel_count = len(image.pixels)
        if image.users > 0 and pixel_count > 0:
            bpy.context.area.spaces.active.image = image
            bpy.ops.image.pack(as_png=True)
            image.name = filename_re.sub(".png", image.name)
            image.packed_files[0].filepath = filename_re.sub(".png",
                                                             image.packed_files[0].filepath)

            bpy.context.area.spaces.active.image = image

            bpy.ops.image.save()
            bpy.ops.image.reload()
            print("+ Packing", image.name, image.filepath)
        else:
            bpy.data.images.remove(image)
    bpy.context.area.type = mode


def unpack_images(images):
    print("#########")
    print(" Unpacking Images ")
    mode = bpy.context.area.type
    bpy.context.area.type = 'IMAGE_EDITOR'
    for image in images:
        bpy.context.area.spaces.active.image = image
        bpy.ops.image.unpack(method='WRITE_LOCAL')
        bpy.ops.image.save()
        bpy.ops.image.reload()
    bpy.context.area.type = mode


def convert_image_to_mask(image, threshold):
    print("Copying image to memory", image.name)
    pixels = list(image.pixels)
    size = len(pixels)

    mode = bpy.context.area.type
    bpy.context.area.type = 'IMAGE_EDITOR'
    bpy.context.area.spaces.active.image = image
    if size == 0:
        return
    pxs = range(0, int(size/4))
    print(" Starting Mask pass")
    for pixel_index in pxs:
        index = pixel_index*4 + 3
        if pixels[index] > threshold:
            pixels[index] = 1
        else:
            pixels[index] = 0
    image.pixels = pixels
    bpy.ops.image.save()
    bpy.context.area.type = mode


def convert_images_to_mask(images, threshold=0.3):
    for image in images:
        convert_image_to_mask(image, threshold)


def clean_textures(material):
    textures = []
    for idx, node in enumerate(material.node_tree.nodes):
        if node is "TEX_IMAGE" and node.texture.image is not None:
            image_path = node.texture.image.filepath_raw
            texture_name = node.name
            print("# Checking", texture_name, image_path)
            if (not node.use or node.texture_coords != "UV"):
                print(" - Removing Texture", texture_name, image_path)
                try:
                    bpy.data.textures.remove(node.texture)
                # catch exception if there are remaining texture users or texture is None
                except (RuntimeError, TypeError):
                    pass
                material.texture_slots.clear(idx)
            else:
                textures.append(node.texture)
    return textures


def get_textures_for_slot(node_tree, texture_type="ALL"):
    print("DEVWARN: DEPRICATED new shader system.")
    texture_list = []
    # for slot in texture_slots:
    #    if slot.image is not None and (texture_type == "ALL" or
    #                                   (texture_type == "COLOR" and slot.use_map_color_diffuse) or
    #                                   (texture_type == "SPECULAR" and (slot.use_map_color_spec or slot.use_map_specular)) or
    #                                   (texture_type == "NORMAL" and slot.use_map_normal) or
    #                                   (texture_type == "ALPHA" and slot.use_map_alpha) or
    #                                   (texture_type == "EMIT" and slot.use_map_emit) or
    #                                   (texture_type == "EMISSION" and slot.use_map_emission) or
    #                                   (texture_type == "HARDNESS" and slot.use_map_hardness) or
    #                                   (texture_type == "ROUGHNESS" and slot.use_map_roughness)) and slot.image not in texture_list:
    #        texture_list.append(slot.image)
    return texture_list



def clean_materials(materials_slots):
    print("TODO: IMPLEMENT ME materials.clean_materials")
    # try:
    #    print("#######################################")
    #    print("Cleaning Materials")

    #    _unique_textures = {}
    #    for material_slot in materials_slots:
    #        if material_slot is not None and material_slot.material is not None:
    #            textures = clean_textures(material_slot.material)

    #            for texture in textures:
    #                if texture is not None:
    #                    if _unique_textures.get(texture.name) is None:
    #                        print("Creating new", texture.name)
    #                        _unique_textures[texture.name] = [
    #                            material_slot.material]
    #                    else:
    #                        print("Appending to", texture.name)
    #                        _unique_textures[texture.name].append(
    #                            material_slot.material)

    #    print("Found", len(_unique_textures.keys()),
    #          "unique textures from", len(materials_slots), "slots")

    #    merge_textures(materials_slots, _unique_textures)
    # except Exception as args:
    #    print("ERROR OCCURRED WHILE TRYING TO PROCESS TEXTURES", args)
    # make_materials_fullbright(materials_slots) # enable this only if fullbright avatars every become supported

# Simulated Hifi PBR
def create_helper_shfpbr_shader_group():
    if (bpy.data.node_groups.find("ePBDSF") is -1):
        print("Attempting to create extended Principled PBR Shader Group")
        group = bpy.data.node_groups.new(name='ePBDSF', type='ShaderNodeTree')
        group_nodes = group.nodes

        group_inputs = group_nodes.new("NodeGroupInput")
        group_inputs.location = (0, 125)

        group_outputs = group_nodes.new("NodeGroupOutput")
        group_outputs.location = (1500, 500)

        #These are mainly to make life simpler for users,
        #  not really actually something that should be done
        roughness_rgb_to_bw = group_nodes.new("ShaderNodeRGBToBW")
        roughness_rgb_to_bw.location = (250, 150) 
        roughness_rgb_to_bw.inputs[0].default_value = (0.8, 0.8, 0.8, 1)
        roughness_rgb_to_bw.hide = True

        roughness_curve_adjust = group_nodes.new("ShaderNodeRGBCurve")
        roughness_curve_adjust.location = (125, 150)
        
        combined_curve = roughness_curve_adjust.mapping.curves[3]
        combined_curve.points.new(0.386368, 0.75)
        roughness_curve_adjust.mapping.update()

        metallic_rgb_to_bw = group_nodes.new("ShaderNodeRGBToBW")
        metallic_rgb_to_bw.location = (250, 250) 
        metallic_rgb_to_bw.inputs[0].default_value = (0, 0, 0, 1)
        metallic_rgb_to_bw.hide = True

        subsurface_rgb_to_bw = group_nodes.new("ShaderNodeRGBToBW")
        subsurface_rgb_to_bw.location = (250, 350) 
        subsurface_rgb_to_bw.inputs[0].default_value = (0, 0, 0, 1)
        subsurface_rgb_to_bw.hide = True

        shader_pbsdf = group_nodes.new("ShaderNodeBsdfPrincipled")
        shader_pbsdf.inputs["Metallic"].default_value = 0
        shader_pbsdf.inputs["Roughness"].default_value = 0
        shader_pbsdf.inputs["Subsurface Color"].default_value = (
            0.98, 0.5, 0.9, 1)
        shader_pbsdf.label = "Custom PBDSF"
        shader_pbsdf.location = (500, 0)

        emit_shader_node = group_nodes.new('ShaderNodeEmission')
        emit_shader_node.name = "EmissionShader"
        emit_shader_node.inputs[0].default_value = (0, 0, 0, 1)
        emit_shader_node.location = (750, 250)

        emit_add_node = group_nodes.new('ShaderNodeAddShader')
        emit_add_node.location = (1000, 250)

        alpha_shader_node = group_nodes.new('ShaderNodeBsdfTransparent')
        alpha_shader_node.name = "AlphaShader"
        alpha_shader_node.inputs[0].default_value = (1, 1, 1, 1)
        alpha_shader_node.location = (1000, 375)

        alpha_mixer_node = group_nodes.new('ShaderNodeMixShader')
        alpha_mixer_node.inputs[0].default_value = 1.0
        alpha_mixer_node.location = (1250, 550)

        links = group.links

        # Alpha Mix
        links.new(alpha_mixer_node.inputs['Fac'], group_inputs.outputs[0])
        links.new(alpha_mixer_node.inputs[1],
                alpha_shader_node.outputs['BSDF'])
        links.new(alpha_mixer_node.inputs[2], emit_add_node.outputs['Shader'])

        # Emission Mix
        links.new(emit_shader_node.inputs['Color'], group_inputs.outputs[1])
        links.new(emit_add_node.inputs[0],
                emit_shader_node.outputs['Emission'])
        links.new(emit_add_node.inputs[1], shader_pbsdf.outputs['BSDF'])

        links.new(shader_pbsdf.inputs['Base Color'], group_inputs.outputs[2])

        #SubSurface Mix
        links.new(subsurface_rgb_to_bw.inputs[0], group_inputs.outputs[3])
        links.new(shader_pbsdf.inputs['Subsurface'], subsurface_rgb_to_bw.outputs[0])

        #Metallic Mix
        links.new(metallic_rgb_to_bw.inputs[0], group_inputs.outputs[4])
        links.new(shader_pbsdf.inputs['Metallic'], metallic_rgb_to_bw.outputs[0])

        # Shininess / Roughness Link
        links.new(roughness_curve_adjust.inputs[1], group_inputs.outputs[5])
        links.new(roughness_rgb_to_bw.inputs[0], roughness_curve_adjust.outputs[0])
        links.new(shader_pbsdf.inputs['Roughness'], roughness_rgb_to_bw.outputs[0])

        links.new(shader_pbsdf.inputs['Normal'], group_inputs.outputs[6])
        links.new(group_outputs.inputs[0], alpha_mixer_node.outputs['Shader'])

        group.inputs[0].name = "Alpha"
        group.inputs[1].name = "Emission"
        group.inputs[2].name = "Diffuse"
        group.inputs[3].name = "Subsurface Scattering"
        group.inputs[4].name = "Metallic"
        group.inputs[5].name = "Roughness"
        group.inputs[6].name = "Normal"
    else:
        print("Shader Group already exist")


def create_new_material():
    current_ui = bpy.context.area.ui_type
    bpy.context.area.ui_type = 'ShaderNodeTree'

    create_helper_shfpbr_shader_group()

    # new material
    mat = bpy.data.materials.new('ePBDSF Material')
    mat.use_nodes = True
    matnodes = mat.node_tree.nodes
    mat.blend_method = 'BLEND'
    mat.show_transparent_back = False

    original = matnodes.get("Principled BSDF")
    matnodes.remove(original)
    output = matnodes.get("Material Output")

    sng = matnodes.new("ShaderNodeGroup")
    sng.node_tree = bpy.data.node_groups['ePBDSF']

    mat.node_tree.links.new(output.inputs[0], sng.outputs["Shader"])

    bpy.context.object.active_material = mat

    bpy.context.area.ui_type = current_ui
    return mat




