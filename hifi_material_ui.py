import bpy

from bpy.props import (
    StringProperty,
    BoolProperty,
    FloatVectorProperty,
    FloatProperty
)

print("Loading Hifi Material Module")


def update_color(self, context):
    mat = context.material
    mat.diffuse_color = mat.hifi_material_color

    
def update_roughness(self, context):
    mat = context.material
    # Hifi values are inverse as Blender Hardness actually defines Glossiness.
    mat.specular_hardness = int((1-(mat.hifi_roughness_float / 100))*512)


def update_metallicness(self, context):
    mat = context.material
    per = mat.hifi_metallic_float/100
    mat.specular_color = (per, per, per)
    

def update_transparency(self, context):
    mat = context.material
    mat.alpha = 1 - mat.hifi_transparency_float/100
    if mat.alpha < 1:
        mat.use_transparency = True
        mat.transparency_method = 'Z_TRANSPARENCY'        
    else:
        mat.use_transparency = False

# Helper functions to make code a bit more readable, and using less large functions that do the same thing
def that_has_diffuse (texture_slot): return texture_slot.use_map_color_diffuse

def that_has_transparency (texture_slot): return texture_slot.use_map_alpha

def that_has_emit (texture_slot): return texture_slot.use_map_emit

def that_has_metallicness (texture_slot): return texture_slot.use_map_color_spec

def that_has_glossiness (texture_slot): return texture_slot.use_map_hardness

def that_has_normal (texture_slot): return texture_slot.use_map_normal


# find first texture in material that has *
# Takes a material context, and uses has_operation function to search for something
def find_first_texture_in(mat, has_operation):
    current_textures = bpy.context.active_object.active_material.texture_slots
    
    found_slot = None
    for texture_slot in current_textures: 
        if texture_slot is not None:
            result = has_operation(texture_slot)
            if result:
                found_slot = texture_slot                           
                break
    
    return found_slot

#TODO: Figure out a cleaner way to do all of this.

class HifiMaterialOperator(bpy.types.Panel):
    bl_idname = "material_helper.hifi"
    bl_label = "High Fidelity Material Helper"
    
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"
    
    COMPAT_ENGINES = {'BLENDER_RENDER'}
    
    bpy.types.Material.hifi_material_color = FloatVectorProperty(
        name = "Tint",
        description = "Set Material Tint",
        default = (0.8, 0.8, 0.8),
        min = 0.0,
        max = 1.0,
        subtype = "COLOR",
        update = update_color
    )
        
    bpy.types.Material.hifi_roughness_float = FloatProperty(
        name = "Roughness",
        description = "Set Roughness",
        default = 30,
        min = 0.0,
        max = 100,
        subtype = "PERCENTAGE",
        update = update_roughness
    )

    bpy.types.Material.hifi_metallic_float = FloatProperty(
        name = "Metallicness",
        description = "Set Metallicness",
        default = 0.0,
        min = 0.0,
        max = 100,
        subtype = "PERCENTAGE",
        update = update_metallicness
    )

    bpy.types.Material.hifi_transparency_float = FloatProperty(
        name = "Transparency",
        description = "Set Transparency",
        default = 0.0,
        min = 0.0,
        max = 100,
        subtype = "PERCENTAGE",
        update = update_transparency
    )
    
    
    @classmethod
    def poll(self, context):
        mat = context.material
        engine = context.scene.render.engine
        print('poll')
        return mat and engine in self.COMPAT_ENGINES
    
        
    def draw (self, context):
        layout = self.layout
        ob = context.active_object     
        material = context.material
        
        row = layout.row()
        
        row.prop(material, "hifi_material_color")             
        row.operator(HifiResetDiffuseOperator.bl_idname)
        
        diffuse = find_first_texture_in(material, that_has_diffuse)
        print('draw')
        if diffuse:
            
            layout.label(text="Diffuse Texture")
            split = layout.split(0.9)
           
            box = split.box()
            box.template_image(diffuse.texture, "image", diffuse.texture.image_user)
            split.operator(HifiDiffuseTextureDeleteOperator.bl_idname, icon='X')
            
        else:
            layout.operator(HifiDiffuseTextureOperator.bl_idname, icon='ZOOMIN')
    
        layout.separator()
        glossiness = find_first_texture_in(material, that_has_glossiness)
        
        if glossiness:          
            
            layout.label(text="Glossiness Texture")
            split = layout.split(0.9)
            box = split.box()
            box.template_image(glossiness.texture, "image", glossiness.texture.image_user)
            split.operator(HifiRoughnessTextureDeleteOperator.bl_idname, icon='X')
            
        else:
            row = layout.row()
            row.prop(material, "hifi_roughness_float")    
            row.operator(HifiRoughnessTextureOperator.bl_idname, icon='ZOOMIN')
        
        
        layout.label(text='Note, Glossiness is inverse of Roughness')
        layout.separator()
        
        metallicness = find_first_texture_in(material, that_has_metallicness)
        
        if metallicness:
            layout.label(text= "Metallicness Texture")
            split = layout.split(0.9)
            box = split.box()
            box.template_image(metallicness.texture, "image", metallicness.texture.image_user)
            split.operator(HifiMetallicTextureDeleteOperator.bl_idname, icon='X')
        else:
            row = layout.row()
            row.prop(material, "hifi_metallic_float")    
            row.operator(HifiMetallicTextureOperator.bl_idname, icon='ZOOMIN')
            
        layout.separator()
        
        normal = find_first_texture_in(material, that_has_normal)
        
        if normal:
            layout.label(text= "Normal Texture")  
            split = layout.split(0.9)
            box = split.box()
            box.template_image(normal.texture, "image", normal.texture.image_user)
            split.operator(HifiNormalTextureDeleteOperator.bl_idname, icon='X')
        else:
            layout.operator(HifiNormalTextureOperator.bl_idname, icon='ZOOMIN')
        
        layout.separator() 
        
        transparency = find_first_texture_in(material, that_has_transparency)
        
        if transparency:
            
            layout.label(text= "Transparency Texture")
            split = layout.split(0.9)
            box = split.box()
            box.template_image(transparency.texture, "image", transparency.texture.image_user)
            split.operator(HifiTransparencyTextureDeleteOperator.bl_idname, icon='X')
        else:
            row = layout.row()
            row.prop(material, "hifi_transparency_float")  
            row.operator(HifiTransparencyTextureOperator.bl_idname, icon='ZOOMIN')
        
        
        layout.separator() 
        emit = find_first_texture_in(material, that_has_emit)
        
        if emit:        
            layout.label(text= "Emit Texture")
            split = layout.split(0.9)
            box = split.box()
            box.template_image(emit.texture, "image", emit.texture.image_user)
            split.operator(HifiEmitTextureDeleteOperator.bl_idname, icon='X')
        else:
            layout.operator(HifiEmitTextureOperator.bl_idname, icon='ZOOMIN')
        
        
       # setattr(mat, "hifi_material_color", mat.diffuse_color)
       # mat.specular_hardness = int((1-(mat.hifi_roughness_float / 100))*512)
       # setattr(mat, "hifi_roughness_float", (1 - mat.specular_hardness / 512) * 100)
       # setattr(mat, "hifi_metallic_float", mat.specular_color[0] * 100)
       # setattr(mat, "hifi_transparency_float")
                    
    
class HifiTexturePreview(bpy.types.Operator):
    bl_idname =  HifiMaterialOperator.bl_idname + "_texture_preview"
    def execute(self, context):
        
        return {'FINISHED'}
        


class HifiResetDiffuseOperator(bpy.types.Operator):
    bl_idname = HifiMaterialOperator.bl_idname + "_diffuse_reset_color"
    bl_label = "Reset Tint"
   
    
    def execute(self, context):
        mat = context.material
        mat.hifi_material_color = (1,1,1)
        mat.diffuse_color = (1,1,1)
        layout = self.layout
        
        return {'FINISHED'}
        
# TODO: lots of repetition here, figure out how to compress and simplifiy.

class HifiDiffuseTextureOperator(bpy.types.Operator):
    bl_idname = HifiMaterialOperator.bl_idname + "_diffuse_texture"
    bl_label = "Add Diffuse"
    
    def execute(self, context):
        layout = self.layout
       
        material = bpy.context.active_object.active_material
        slots = bpy.context.active_object.active_material.texture_slots
        found_slot = find_first_texture_in(material, that_has_diffuse)
        
        if found_slot is None:
            name = material.name + '_diffuse'
            texture = bpy.data.textures.new(name, 'IMAGE')
            slot = slots.add()
            slot.texture = texture
        
        
        return {'FINISHED'}
    
     
class HifiDiffuseTextureDeleteOperator(bpy.types.Operator):
    bl_idname = HifiMaterialOperator.bl_idname + "_diffuse_texture_delete"
    bl_label = ""
    
    def execute(self, context):
        material = bpy.context.active_object.active_material
        slots = bpy.context.active_object.active_material.texture_slots
        found_slot = find_first_texture_in(material, that_has_diffuse)
        # TODO: Investigate an actual method to delete a texture. Its harder than it looks
        if found_slot:
            found_slot.use_map_color_diffuse = False
                
        return {'FINISHED'}
    
    
class HifiRoughnessTextureOperator(bpy.types.Operator):
    bl_idname = HifiMaterialOperator.bl_idname + "_glossiness_texture"
    bl_label = "Add Glossiness"
    
    def execute(self, context):
        material = bpy.context.active_object.active_material
        slots = bpy.context.active_object.active_material.texture_slots
        found_slot = find_first_texture_in(material, that_has_glossiness)
        
        
        if found_slot is None:
            name = material.name + '_glossiness'
            texture = bpy.data.textures.new(name, 'IMAGE')
            slot = slots.add()
            slot.use_map_hardness = True
            slot.use_map_color_diffuse = False
            slot.texture = texture
        
        return {'FINISHED'}
    
     
class HifiRoughnessTextureDeleteOperator(bpy.types.Operator):
    bl_idname = HifiMaterialOperator.bl_idname + "_glossiness_texture_delete"
    bl_label = ""
    
    def execute(self, context):
        material = bpy.context.active_object.active_material
        slots = bpy.context.active_object.active_material.texture_slots
        found_slot = find_first_texture_in(material, that_has_glossiness)
        # TODO: Investigate an actual method to delete a texture. Its harder than it looks
        if found_slot:
            found_slot.use_map_hardness = False
                
        return {'FINISHED'}
    
    
class HifiMetallicTextureOperator(bpy.types.Operator):
    bl_idname = HifiMaterialOperator.bl_idname + "_metallic_texture"
    bl_label = "Add Metallicness"
    
    def execute(self, context):
        material = bpy.context.active_object.active_material
        slots = bpy.context.active_object.active_material.texture_slots
        found_slot = find_first_texture_in(material, that_has_metallicness)
        
        if found_slot is None:
            name = material.name + '_metallicness'
            texture = bpy.data.textures.new(name, 'IMAGE')
            slot = slots.add()
            slot.use_map_color_spec = True
            slot.use_map_color_diffuse = False
            slot.texture = texture
        
        return {'FINISHED'}
    
    
class HifiMetallicTextureDeleteOperator(bpy.types.Operator):
    bl_idname = HifiMaterialOperator.bl_idname + "_metallic_texture_delete"
    bl_label = ""

    def execute(self, context):
        material = bpy.context.active_object.active_material
        slots = bpy.context.active_object.active_material.texture_slots
        found_slot = find_first_texture_in(material, that_has_metallicness)
        # TODO: Investigate an actual method to delete a texture. Its harder than it looks
        if found_slot:
            found_slot.use_map_color_spec = False
                
        return {'FINISHED'}


class HifiNormalTextureOperator(bpy.types.Operator):
    bl_idname = HifiMaterialOperator.bl_idname + "_normal_texture"
    bl_label = "Add Normal"
    
    def execute(self, context):
        material = bpy.context.active_object.active_material
        slots = bpy.context.active_object.active_material.texture_slots
        found_slot = find_first_texture_in(material, that_has_normal)
        
        if found_slot is None:
            name = material.name + '_normal'
            texture = bpy.data.textures.new(name, 'IMAGE')
            slot = slots.add()
            texture.use_normal_map = True
            slot.use_map_normal = True
            slot.use_map_color_diffuse = False
            slot.texture = texture
            
            
        return {'FINISHED'}
    
    
class HifiNormalTextureDeleteOperator(bpy.types.Operator):
    bl_idname = HifiMaterialOperator.bl_idname + "_normal_texture_delete"
    bl_label = ""

    def execute(self, context):
        material = bpy.context.active_object.active_material
        slots = bpy.context.active_object.active_material.texture_slots
        found_slot = find_first_texture_in(material, that_has_normal)
        # TODO: Investigate an actual method to delete a texture. Its harder than it looks
        if found_slot:
            found_slot.use_map_normal = False
                
        return {'FINISHED'}


class HifiTransparencyTextureOperator(bpy.types.Operator):
    bl_idname = HifiMaterialOperator.bl_idname + "_transparency_texture"
    bl_label = "Add Transparency"
    
    def execute(self, context):
        material = bpy.context.active_object.active_material
        slots = bpy.context.active_object.active_material.texture_slots
        found_slot = find_first_texture_in(material, that_has_transparency)
        
        if found_slot is None:
            name = material.name + '_transparency'
            texture = bpy.data.textures.new(name, 'IMAGE')
            slot = slots.add()
            slot.use_map_alpha = True
            slot.use_map_color_diffuse = False
            slot.texture = texture
            
            
        return {'FINISHED'}
    
class HifiTransparencyTextureDeleteOperator(bpy.types.Operator):
    bl_idname = HifiMaterialOperator.bl_idname + "_transparency_texture_delete"
    bl_label = ""

    def execute(self, context):
        material = bpy.context.active_object.active_material
        slots = bpy.context.active_object.active_material.texture_slots
        found_slot = find_first_texture_in(material, that_has_transparency)
        # TODO: Investigate an actual method to delete a texture. Its harder than it looks
        if found_slot:
            found_slot.use_map_alpha = False
                
        return {'FINISHED'}

    
class HifiEmitTextureOperator(bpy.types.Operator):
    bl_idname = HifiMaterialOperator.bl_idname + "_emit_texture"
    bl_label = "Add Emit"
    
    def execute(self, context):
        material = bpy.context.active_object.active_material
        slots = bpy.context.active_object.active_material.texture_slots
        found_slot = find_first_texture_in(material, that_has_emit)
        
        if found_slot is None:
            name = material.name + '_emit'
            texture = bpy.data.textures.new(name, 'IMAGE')
            slot = slots.add()
            slot.use_map_emit = True
            slot.use_map_color_diffuse = False
            slot.texture = texture
            
        return {'FINISHED'}
    

class HifiEmitTextureDeleteOperator(bpy.types.Operator):
    bl_idname = HifiMaterialOperator.bl_idname + "_emit_texture_delete"
    bl_label = ""

    def execute(self, context):
        material = bpy.context.active_object.active_material
        slots = bpy.context.active_object.active_material.texture_slots
        found_slot = find_first_texture_in(material, that_has_emit)
        # TODO: Investigate an actual method to delete a texture. Its harder than it looks
        if found_slot:
            found_slot.use_map_emit = False
                
        return {'FINISHED'}
    
    
    
classes = [
    HifiResetDiffuseOperator,
    HifiDiffuseTextureOperator,
    HifiDiffuseTextureDeleteOperator,
    HifiRoughnessTextureOperator,
    HifiRoughnessTextureDeleteOperator,
    HifiMetallicTextureOperator,
    HifiMetallicTextureDeleteOperator,
    HifiNormalTextureOperator,
    HifiNormalTextureDeleteOperator,
    HifiTransparencyTextureOperator,
    HifiTransparencyTextureDeleteOperator,
    HifiEmitTextureOperator,
    HifiEmitTextureDeleteOperator,
    HifiMaterialOperator
]

def register():
    for cls in classes:    
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:    
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()