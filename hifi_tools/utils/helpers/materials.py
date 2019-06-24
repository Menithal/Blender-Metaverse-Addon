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
from bpy_extras.node_shader_utils import (
    ShaderWrapper, ShaderImageTextureWrapper,
    _set_check, rgb_to_rgba, rgba_to_rgb
)
from bpy.app.handlers import persistent
import hifi_tools
from mathutils import Euler


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
        bpy.ops.metaverse_toolset_messages.remind_save('INVOKE_DEFAULT')
        return

    if pack_images(images):
        unpack_images(images)


def pack_images(images):
    mode = bpy.context.area.type
    success = False
    try:
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
        success = True

    except Exception as e:
        print("Error: Pack Images - Did not succeed")
    bpy.context.area.type = mode

    return success


def unpack_images(images):
    print("#########")
    success = False
    try:
        mode = bpy.context.area.type
        bpy.context.area.type = 'IMAGE_EDITOR'
        for image in images:
            bpy.context.area.spaces.active.image = image
            bpy.ops.image.unpack(method='WRITE_LOCAL')
            bpy.ops.image.save()
            bpy.ops.image.reload()
        success = True

    except Exception as e:
        print("Error: Unpacking Images - Did not succeed")

    bpy.context.area.type = mode
    return success


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

    if image.source != "GENERATED":
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


def clean_materials(materials_slots):
    print("TODO: IMPLEMENT ME materials.clean_materials")


def rgb_to_bw(rgb):
    return (rgb[0] + rgb[1] + rgb[2])/3


def correct_node_color_space_to_non_color(input_node, index=0):
    if input_node is None:
        return None

    links = input_node.links

    if links is None or len(links) == 0:
        return None

    image_node = links[index].from_node

    if image_node.type == "TEX_IMAGE":
        image_node.image.colorspace_settings.name = "Non-Color"


@persistent
def correct_all_color_spaces_to_non_color(context):
    user_preferences = bpy.context.preferences
    addon_prefs = user_preferences.addons[hifi_tools.__name__].preferences
    colorspaces_on_save = addon_prefs.get("automatic_color_space_fix")

    if colorspaces_on_save is None:
        colorspaces_on_save = True
        addon_prefs["automatic_color_space_fix"] = True

    if colorspaces_on_save:
        print("Colorspace corrections")
        for mat in bpy.data.materials:
            node = get_principled_bsdf_shader(mat.node_tree.nodes)
            if node is not None:
                correct_node_color_space_to_non_color(
                    node.inputs.get("Metallic"))
                correct_node_color_space_to_non_color(
                    node.inputs.get("Roughness"))
                correct_node_color_space_to_non_color(
                    node.inputs.get("Subsurface Scattering"))
                normal_map_socket = node.inputs.get("Normal")

                if normal_map_socket is not None:
                    normal_map = normal_map_socket.links[0].from_node
                    correct_node_color_space_to_non_color(
                        normal_map.inputs.get("Color"))


class HifiShaderWrapper(ShaderWrapper):
    """
    Hard coded shader setup, based in Principled BSDF.
    Should cover most common cases on import, and gives a basic nodal shaders support for export.
    Supports basic: diffuse/spec/reflect/transparency/normal, with texturing.
    """

    NODES_LIST = (
        "node_out",
        "node_principled_bsdf",

        "_node_normalmap",
        "_node_texcoords",
    )

    __slots__ = (
        "is_readonly",
        "material",
        *NODES_LIST,
    )

    NODES_LIST = ShaderWrapper.NODES_LIST + NODES_LIST

    def __init__(self, material, is_readonly=True, use_nodes=True):
        super(HifiShaderWrapper, self).__init__(
            material, is_readonly, use_nodes)

    def update(self):
        super(HifiShaderWrapper, self).update()

        if not self.use_nodes:
            return

        tree = self.material.node_tree

        nodes = tree.nodes
        links = tree.links

        # --------------------------------------------------------------------
        # Main output and shader.
        node_out = None
        node_principled = None
        for n in nodes:
            if n.bl_idname == 'ShaderNodeOutputMaterial' and n.inputs[0].is_linked:
                node_out = n
                node_principled = n.inputs[0].links[0].from_node
            elif n.bl_idname == 'ShaderNodeBsdfPrincipled' and n.outputs[0].is_linked:
                node_principled = n
                for lnk in n.outputs[0].links:
                    node_out = lnk.to_node
                    if node_out.bl_idname == 'ShaderNodeOutputMaterial':
                        break
            if (
                    node_out is not None and node_principled is not None and
                    node_out.bl_idname == 'ShaderNodeOutputMaterial' and
                    node_principled.bl_idname == 'ShaderNodeBsdfPrincipled'
            ):
                break
            node_out = node_principled = None  # Could not find a valid pair, let's try again

        if node_out is not None:
            self._grid_to_location(0, 0, ref_node=node_out)
        elif not self.is_readonly:
            node_out = nodes.new(type='ShaderNodeOutputMaterial')
            node_out.label = "Material Out"
            node_out.target = 'ALL'
            self._grid_to_location(1, 1, dst_node=node_out)
        self.node_out = node_out

        if node_principled is not None:
            self._grid_to_location(0, 0, ref_node=node_principled)
        elif not self.is_readonly:
            node_principled = nodes.new(type='ShaderNodeBsdfPrincipled')
            node_principled.label = "Principled BSDF"
            self._grid_to_location(0, 1, dst_node=node_principled)
            # Link
            links.new(node_principled.outputs["BSDF"],
                      self.node_out.inputs["Surface"])
        self.node_principled_bsdf = node_principled

        # --------------------------------------------------------------------
        # Normal Map, lazy initialization...
        self._node_normalmap = ...

        # --------------------------------------------------------------------
        # Tex Coords, lazy initialization...
        self._node_texcoords = ...

    def node_normalmap_get(self):
        if not self.use_nodes or self.node_principled_bsdf is None:
            return None
        node_principled = self.node_principled_bsdf
        if self._node_normalmap is ...:
            # Running only once, trying to find a valid normalmap node.
            if node_principled.inputs["Normal"].is_linked:
                node_normalmap = node_principled.inputs["Normal"].links[0].from_node
                if node_normalmap.bl_idname == 'ShaderNodeNormalMap':
                    self._node_normalmap = node_normalmap
                    self._grid_to_location(0, 0, ref_node=node_normalmap)
            if self._node_normalmap is ...:
                self._node_normalmap = None
        if self._node_normalmap is None and not self.is_readonly:
            tree = self.material.node_tree
            nodes = tree.nodes
            links = tree.links

            node_normalmap = nodes.new(type='ShaderNodeNormalMap')
            node_normalmap.label = "Normal/Map"
            self._grid_to_location(-1, -2, dst_node=node_normalmap,
                                   ref_node=node_principled)
            # Link
            links.new(node_normalmap.outputs["Normal"],
                      node_principled.inputs["Normal"])
            self._node_normalmap = node_normalmap
        return self._node_normalmap

    node_normalmap = property(node_normalmap_get)

    # --------------------------------------------------------------------
    # Base Color.

    def base_color_get(self):
        if not self.use_nodes or self.node_principled_bsdf is None:
            return self.material.diffuse_color
        return rgba_to_rgb(self.node_principled_bsdf.inputs["Base Color"].default_value)

    @_set_check
    def base_color_set(self, color):
        color = rgb_to_rgba(color)
        self.material.diffuse_color = color
        if self.use_nodes and self.node_principled_bsdf is not None:
            self.node_principled_bsdf.inputs["Base Color"].default_value = color

    base_color = property(base_color_get, base_color_set)

    def base_color_texture_get(self):
        if not self.use_nodes or self.node_principled_bsdf is None:
            return None
        return ShaderImageTextureWrapper(
            self, self.node_principled_bsdf,
            self.node_principled_bsdf.inputs["Base Color"],
            grid_row_diff=1,
        )

    base_color_texture = property(base_color_texture_get)

    # --------------------------------------------------------------------
    # Specular.

    def specular_get(self):
        if not self.use_nodes or self.node_principled_bsdf is None:
            return self.material.specular_intensity
        return self.node_principled_bsdf.inputs["Specular"].default_value

    @_set_check
    def specular_set(self, value):
        self.material.specular_intensity = value
        if self.use_nodes and self.node_principled_bsdf is not None:
            self.node_principled_bsdf.inputs["Specular"].default_value = value

    specular = property(specular_get, specular_set)

    def specular_tint_get(self):
        if not self.use_nodes or self.node_principled_bsdf is None:
            return 0.0
        return self.node_principled_bsdf.inputs["Specular Tint"].default_value

    @_set_check
    def specular_tint_set(self, value):
        if self.use_nodes and self.node_principled_bsdf is not None:
            self.node_principled_bsdf.inputs["Specular Tint"].default_value = value

    specular_tint = property(specular_tint_get, specular_tint_set)

    # Will only be used as gray-scale one...

    def specular_texture_get(self):
        if not self.use_nodes or self.node_principled_bsdf is None:
            print("NO NODES!")
            return None
        return ShaderImageTextureWrapper(
            self, self.node_principled_bsdf,
            self.node_principled_bsdf.inputs["Specular"],
            grid_row_diff=0,
        )

    specular_texture = property(specular_texture_get)

    # --------------------------------------------------------------------
    # Roughness (also sort of inverse of specular hardness...).

    def roughness_get(self):
        if not self.use_nodes or self.node_principled_bsdf is None:
            return self.material.roughness
        return self.node_principled_bsdf.inputs["Roughness"].default_value

    @_set_check
    def roughness_set(self, value):
        self.material.roughness = value
        if self.use_nodes and self.node_principled_bsdf is not None:
            self.node_principled_bsdf.inputs["Roughness"].default_value = value

    roughness = property(roughness_get, roughness_set)

    # Will only be used as gray-scale one...

    def roughness_texture_get(self):
        if not self.use_nodes or self.node_principled_bsdf is None:
            return None
        return ShaderImageTextureWrapper(
            self, self.node_principled_bsdf,
            self.node_principled_bsdf.inputs["Roughness"],
            grid_row_diff=0,
        )

    roughness_texture = property(roughness_texture_get)

    # --------------------------------------------------------------------
    # Metallic (a.k.a reflection, mirror).

    def metallic_get(self):
        if not self.use_nodes or self.node_principled_bsdf is None:
            return self.material.metallic
        return self.node_principled_bsdf.inputs["Metallic"].default_value

    @_set_check
    def metallic_set(self, value):
        self.material.metallic = value
        if self.use_nodes and self.node_principled_bsdf is not None:
            self.node_principled_bsdf.inputs["Metallic"].default_value = value

    metallic = property(metallic_get, metallic_set)

    # Will only be used as gray-scale one...

    def metallic_texture_get(self):
        if not self.use_nodes or self.node_principled_bsdf is None:
            return None
        return ShaderImageTextureWrapper(
            self, self.node_principled_bsdf,
            self.node_principled_bsdf.inputs["Metallic"],
            grid_row_diff=0,
        )

    metallic_texture = property(metallic_texture_get)

    # --------------------------------------------------------------------
    # Transparency settings.

    def ior_get(self):
        if not self.use_nodes or self.node_principled_bsdf is None:
            return 1.0
        return self.node_principled_bsdf.inputs["IOR"].default_value

    @_set_check
    def ior_set(self, value):
        if self.use_nodes and self.node_principled_bsdf is not None:
            self.node_principled_bsdf.inputs["IOR"].default_value = value

    ior = property(ior_get, ior_set)

    # Will only be used as gray-scale one...

    def ior_texture_get(self):
        if not self.use_nodes or self.node_principled_bsdf is None:
            return None
        return ShaderImageTextureWrapper(
            self, self.node_principled_bsdf,
            self.node_principled_bsdf.inputs["IOR"],
            grid_row_diff=-1,
        )

    ior_texture = property(ior_texture_get)

    def transmission_get(self):
        if not self.use_nodes or self.node_principled_bsdf is None:
            return 0.0
        return self.node_principled_bsdf.inputs["Transmission"].default_value

    @_set_check
    def transmission_set(self, value):
        if self.use_nodes and self.node_principled_bsdf is not None:
            self.node_principled_bsdf.inputs["Transmission"].default_value = value

    transmission = property(transmission_get, transmission_set)

    # Will only be used as gray-scale one...

    def transmission_texture_get(self):
        if not self.use_nodes or self.node_principled_bsdf is None:
            return None
        return ShaderImageTextureWrapper(
            self, self.node_principled_bsdf,
            self.node_principled_bsdf.inputs["Transmission"],
            grid_row_diff=-1,
        )

    transmission_texture = property(transmission_texture_get)

    def alpha_get(self):
        if not self.use_nodes or self.node_principled_bsdf is None:
            return 1.0
        return self.node_principled_bsdf.inputs["Alpha"].default_value

    @_set_check
    def alpha_set(self, value):
        if self.use_nodes and self.node_principled_bsdf is not None:
            self.node_principled_bsdf.inputs["Alpha"].default_value = value

    alpha = property(alpha_get, alpha_set)

    # Will only be used as gray-scale one...

    def alpha_texture_get(self):
        if not self.use_nodes or self.node_principled_bsdf is None:
            return None
        return ShaderImageTextureWrapper(
            self, self.node_principled_bsdf,
            self.node_principled_bsdf.inputs["Alpha"],
            grid_row_diff=-1,
        )

    alpha_texture = property(alpha_texture_get)

    # --------------------------------------------------------------------
    # Normal map.

    def normalmap_strength_get(self):
        if not self.use_nodes or self.node_normalmap is None:
            return 0.0
        return self.node_normalmap.inputs["Strength"].default_value

    @_set_check
    def normalmap_strength_set(self, value):
        if self.use_nodes and self.node_normalmap is not None:
            self.node_normalmap.inputs["Strength"].default_value = value

    normalmap_strength = property(
        normalmap_strength_get, normalmap_strength_set)

    def normalmap_texture_get(self):
        if not self.use_nodes or self.node_normalmap is None:
            return None
        return ShaderImageTextureWrapper(
            self, self.node_normalmap,
            self.node_normalmap.inputs["Color"],
            grid_row_diff=-2,
        )

    normalmap_texture = property(normalmap_texture_get)

    def emission_get(self):
        if not self.use_nodes or self.node_principled_bsdf is None:
            return 1.0
        return self.node_principled_bsdf.inputs["Emission"].default_value

    @_set_check
    def emission_set(self, value):
        if self.use_nodes and self.node_principled_bsdf is not None:
            self.node_principled_bsdf.inputs["Emission"].default_value = value

    emissive = property(emission_get, emission_set)

    # Will only be used as gray-scale one...

    def emission_texture_get(self):
        if not self.use_nodes or self.node_principled_bsdf is None:
            return None
        return ShaderImageTextureWrapper(
            self, self.node_principled_bsdf,
            self.node_principled_bsdf.inputs["Emission"],
            grid_row_diff=-1,
        )

    emission_texture = property(emission_texture_get)


def get_principled_bsdf_shader(nodes):
    for node in nodes: 
        if node.type == "BSDF_PRINCIPLED":
                return node
    return False

def find_existing_mapping(nodes):
    for node in nodes: 
        if node.type == "MAPPING":
                return node
    return False

def find_env_texture(nodes):
    for node in nodes: 
        if node.type == "TEX_ENVIRONMENT":
                return node
    return False

def fix_env_rotations():
    try:

        for world in bpy.data.worlds:
            nodes = world.node_tree.nodes
            links = world.node_tree.links
            mapping = find_existing_mapping(nodes)
            env = find_env_texture(nodes)
            
            if mapping == False and env != False:
                
                texture_coordinates = nodes.new("ShaderNodeTexCoord")
                texture_coordinates.location = (-800, 145)
                mapper = nodes.new("ShaderNodeMapping")
                mapper.location = (-625, 145)
                
                mapper.rotation = Euler((0.0, 0.0, 1.5707963705062866), 'XYZ')
                
                links.new(mapper.inputs[0], texture_coordinates.outputs["Object"])
                links.new(env.inputs[0], mapper.outputs[0])
            
    except Exception as e:
        print (e)
        