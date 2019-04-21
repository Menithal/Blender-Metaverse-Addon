import bpy
from bpy_extras.node_shader_utils import ShaderWrapper, ShaderImageTextureWrapper, _set_check, rgb_to_rgba, rgba_to_rgb

def get_epbdsf_node(material):
    for node in material.node_tree.nodes:
        if node.type == 'GROUP' and node.node_tree == bpy.data.node_groups['ePBDSF']:
            return node
    
    return None


def rgb_to_bw(rgb):
    return (rgb[0] + rgb[1] + rgb[2])/3

class ePBSDFWrapper(ShaderWrapper):
    
    def __init__(self, material, is_readonly=True, use_nodes=True):
        super(ePBSDFWrapper, self).__init__(material, is_readonly, use_nodes)

    def update(self):
        super(ePBSDFWrapper, self).update()

        if not self.use_nodes:
            return

        tree = self.material.node_tree
        nodes = tree.nodes
        
        node_out = None
        node_group = None
        
        for node in nodes:
            if node.bl_idname == 'ShaderNodeOutputMaterial' and node.inputs[0].is_linked:
                node_out = node
                node_group = node.inputs[0].links[0].from_node
                ## Check Links
                
            elif node.bl_idname == 'ShaderNodeGroup' and node.node_tree == bpy.data.node_groups['ePBDSF']:
                node_group = node
                node_out = node.outputs[0].links[0].to_node
                    
            if node_group is not None and node_out is not None:
                if node_group.outputs[0].links[0].to_node == node_out:
                    break
                
            node_out = node_group = None ## Reset, No valid pair found yet.
        
        
        self.node_group = node_group
        ## If No Texture is set, fall back on default.
        
        self._node_normalmap = ...
        self._node_texcoords = ...
        
    def normalmap_get(self):
        if not self.use_nodes or self.node_group is None:
            return None
        
        node_group = self.node_group
        if self._node_normalmap is ...:
            if node_group.inputs["Normal"].is_linked:
                node_normalmap = node_group.inputs["Normal"].links[0].from_node
                if node_normalmap.bl_idname == 'ShaderNodeNormalMap':
                    self._node_normalmap = node_normalmap
                    #self._grid_to_location(0, 0, ref_node=node_normalmap)
            if self._node_normalmap is ...:
                self._node_normalmap = None
     
        return self._node_normalmap

    normalmap = property(normalmap_get) # this is found by hifi.
    
    def base_color_get(self):
        if not self.use_nodes or self.node_group is None:
            return self.material.diffuse_color
        return rgba_to_rgb(self.node_group.inputs["Diffuse"].default_value)
    
    @_set_check
    def base_color_set(self, color):
        color = rgb_to_rgba(color)
        self.material.diffuse_color = color
        if self.use_nodes and self.node_group is not None:
            self.node_group.inputs["Diffuse"].default_value = color

    base_color = property(base_color_get, base_color_set)
    
    
    def base_color_texture_get(self):
        if not self.use_nodes or self.node_group is None:
            return None
        return ShaderImageTextureWrapper(
            self, self.node_group,
            self.node_group.inputs["Diffuse"],
            grid_row_diff=1,
        )

    color_map = property(base_color_texture_get)
    
    
    def roughness_get(self):
        if not self.use_nodes or self.node_group is None:
            return None
        return rgb_to_bw(self.node_group.inputs["Roughness"].default_value)

    @_set_check
    def roughness_set(self, value):
        self.material.roughness = value
        if self.use_nodes and self.node_group is not None:
            self.node_group.inputs["Roughness"].default_value = value

    roughness = property(roughness_get, roughness_set)
    
    
    def roughness_texture_get(self):
        if not self.use_nodes or self.node_group is None:
            return None
        return ShaderImageTextureWrapper(
            self, self.node_group,
            self.node_group.inputs["Roughness"],
            grid_row_diff=0,
        )

    roughness_map = property(roughness_texture_get)

    
    def metallic_get(self):
        if not self.use_nodes or self.node_group is None:
            return rgb_to_bw(self.material.metallic)
        return rgb_to_bw(self.node_group.inputs["Metallic"].default_value)

    @_set_check
    def metallic_set(self, value):
        self.material.metallic = value
        if self.use_nodes and self.node_group is not None:
            self.node_group.inputs["Metallic"].default_value = value

    metallic = property(metallic_get, metallic_set)
    
    
    # Will only be used as gray-scale one...
    def metallic_texture_get(self):
        if not self.use_nodes or self.node_group is None:
            return None
        return ShaderImageTextureWrapper(
            self, self.node_group,
            self.node_group.inputs["Metallic"],
            grid_row_diff=0,
        )

    metallic_map = property(metallic_texture_get)
    
    def transparency_get(self):
        if not self.use_nodes or self.node_group is None:
            return 0.0
        return self.node_group.inputs["Alpha"].default_value

    @_set_check
    def transparency_set(self, value):
        self.material.metallic = value
        if self.use_nodes and self.node_group is not None:
            self.node_group.inputs["Alpha"].default_value = value

    transparency = property(transparency_get, transparency_set)
    
    
    # Will only be used as gray-scale one...
    def transparency_texture_get(self):
        if not self.use_nodes or self.node_group is None:
            return None
        return ShaderImageTextureWrapper(
            self, self.node_group,
            self.node_group.inputs["Alpha"],
            grid_row_diff=0,
        )
    # dubious
    transparency_texture = property(transparency_texture_get)


    def emissive_get(self):
        if not self.use_nodes or self.node_group is None:
            return 0.0
        return self.node_group.inputs["Emission"].default_value

    @_set_check
    def emissive_set(self, value):
        self.material.metallic = value
        if self.use_nodes and self.node_group is not None:
            self.node_group.inputs["Emission"].default_value = value

    emissive = property(emissive_get, emissive_set)
    
    
    # Will only be used as gray-scale one...
    def emissive_texture_get(self):
        if not self.use_nodes or self.node_group is None:
            return None
        return ShaderImageTextureWrapper(
            self, self.node_group,
            self.node_group.inputs["Emission"],
            grid_row_diff=0,
        )

    emissive_map = property(emissive_texture_get)


    def normalmap_strength_get(self):
        if not self.use_nodes or self.node_normalmap is None:
            return 0.0
        return self.node_normalmap.inputs["Strength"].default_value

    @_set_check
    def normalmap_strength_set(self, value):
        if self.use_nodes and self.node_normalmap is not None:
            self.node_normalmap.inputs["Strength"].default_value = value

    normalmap_strength = property(normalmap_strength_get, normalmap_strength_set)

    def normalmap_texture_get(self):
        if not self.use_nodes or self.normalmap is None:
            return None
        return ShaderImageTextureWrapper(
            self, self.normalmap,
            self.normalmap.inputs["Color"],
            grid_row_diff=-2,
        )

    normal_map = property(normalmap_texture_get)


    