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

# Scene Logic for Parsing and Navigating Content Tree
# By Matti 'Menithal' Lahtinen



from math import sqrt, acos, pow, sin, cos
from hashlib import md5
from mathutils import Quaternion, Vector, Euler, Matrix
from hifi_primitives import *


NEAREST_DIGIT = 10000
'x,y,z'
ZERO_VECTOR = (0,0,0)
'x,y,z'
PIVOT_VECTOR = (0.5,0.5,0.5)
'w,x,y,z'
ZERO_QUAT = (1,0,0,0)

def round_nearest(val):
    return round(val * NEAREST_DIGIT)/NEAREST_DIGIT

def parse_dict_vector(entity, index, default = ZERO_VECTOR):
    if index in entity:
        vect = entity[index]
        return (round_nearest(vect['x']), round_nearest(vect['y']), round_nearest(vect['z']))
    else:
        return default


def parse_dict_quaternion(entity, index):
    if index in entity:
        quat = entity[index]
        return (quat['w'],quat['x'],quat['y'],quat['z'])
    else:
        return ZERO_QUAT


def swap_pivot(v):
    return Vector(((v[0] - PIVOT_VECTOR[0]), (v[2] - PIVOT_VECTOR[1]), -(v[1] - PIVOT_VECTOR[2])))
    
    
def swap_yz(v):
    return Vector((v[0], v[2], v[1]))


def swap_nyz(vector):
    return Vector((vector[0], -vector[2], vector[1]))


def quat_swap_nyz(q):
    q1 = Quaternion(q)
        
    factor = sqrt(2)/2
    
    axis = q1.axis
    angle = q1.angle
    
    temp = axis.z
    axis.z = axis.y
    axis.y = -temp
    return Quaternion(axis, angle)


class HifiScene:
    def __init__(self, json, 
              uv_sphere = False,
              join_children=True, 
              merge_distance = 0.01, 
              delete_interior_faces = True,
              use_boolean_operation = "NONE"):
        json_entities = json['Entities']

        self.uv_sphere = uv_sphere
        self.join_children = join_children
        self.merge_distance = merge_distance
        self.delete_interior_faces = delete_interior_faces
        self.use_boolean_operation = use_boolean_operation
        
        self.entities = []
        self.materials = []
        self.entity_ids = []
        self.material_index = []
        self.materials = []
        self.parent_entities = []
        
        self.root = []
        
        # Build Indices
        print( ' building indices ')
        for idx, entity in enumerate(json_entities):
            self.entity_ids.append(entity['id'])   
            hifi_entity = HifiObject(entity, self)
            self.entities.append(hifi_entity)
        
        # Build Trees
        print( ' building parents ')
        for entity in self.entities:
            self.append_parent(entity)
            
                
        self.build_scene()
        

    ## put this outside of this.
    def build_scene(self):
        current_context = bpy.context.area.type 
        bpy.context.area.type = 'VIEW_3D'

        bpy.context.space_data.cursor_location[0] = 0.0
        bpy.context.space_data.cursor_location[1] = 0.0
        bpy.context.space_data.cursor_location[2] = 0.0
        bpy.context.area.type = current_context
        print("Building Scene out of " + str(len(self.entities)) + ' Objects and '
             + str(len(self.material_index)) + ' materials')
            
        for entity in self.entities:
            if entity.is_root():
                entity.build()
                
    
    def append_parent(self, entity):
        result = self.search_entity(entity.parent_id) 
        if result is not None:
            result.add_child(entity)
            entity.set_parent(result)
    
    
    def search_entity(self, id):
        # May need to do some more advanced tricks here maybe later.
        found_entity = None
        try:
            index = self.entity_ids.index(id)
            found_entity = self.entities[index]
        except e:
            pass
        finally:
            return found_entity
            
        
    def append_material(self, color):
        # Just Hash result
    
        material_hash = md5(str(color[0] + color[1] << 2+ color[2]<<4 ).encode('utf-8')).hexdigest()
        
        if material_hash not in self.material_index:
            index = len(self.material_index)
            self.material_index.append(material_hash)
            
            mat = bpy.data.materials.new(str(color))
            ## convert from rgb to float
            mat.diffuse_color = tuple(c/255 for c in color)
            
            ## Make sure material at first is not metallic
            mat.specular_color = (0,0,0)
            
            self.materials.append(mat)  
            return mat
        
        return self.materials[self.material_index.index(material_hash)]


class HifiObject:

    def __init__(self, entity, scene):
        
        self.id = entity['id']
        self.children = []
        self.blender_object = None
        self.scene = scene
        # Make sure the Blender Object has a name    
        if 'name' in entity and len(entity['name'].strip()) > 0:
            self.name = entity['name'] + '-' + self.id
        elif 'shape' in entity:
            self.name = entity['shape']  + '-' + self.id
        else:
            self.name = entity['type'] + '-' + self.id
        
        self.position_original = Vector(parse_dict_vector(entity, 'position'))
        self.position = swap_nyz(parse_dict_vector(entity, 'position'))
        
        self.pivot = swap_pivot(parse_dict_vector(entity, 'registrationPoint', PIVOT_VECTOR))    
        self.dimensions = swap_yz(parse_dict_vector(entity, 'dimensions'))
        
        self.rotation_original = Quaternion(parse_dict_quaternion(entity, 'rotation'))
        self.rotation = quat_swap_nyz(parse_dict_quaternion(entity, 'rotation'))

        self.parent = None
        self.children = []       
        
        if 'parentID' in entity:
            self.parent_id = entity['parentID']
        else:
            self.parent_id = None

        self.type = entity['type']
        self.shape = None
        if 'shape' in entity:
            self.shape = entity['shape']

        if self.type != 'Light' and self.type != 'Zone' and self.type != 'Particle':
            if 'color' in entity:
                color = entity['color']
                self.material = scene.append_material((color['red'], color['green'], color['blue']))
        else:
            self.material = None
            

    def is_root(self):
        if self.parent is  None:
            return True
        return False
    
    def select(self):
        self.blender_object.select = True
            

    def build(self):
        # Type Logic Here
        for child in self.children:
            child.build()
        
        if self.type == 'Box' or self.type == 'Shape':
            if self.shape == 'Cube':
                add_box(self)
            elif self.shape == 'Icosahedron':
                add_icosahedron(self)
            elif self.shape == 'Dodecahedron':
                add_docadehedron(self)
            elif self.shape == 'Cylinder':
                add_cylinder(self)
            elif self.shape == 'Octagon':
                add_octagon(self)
            elif self.shape == 'Hexagon':
                add_hexagon(self)
            elif self.shape == 'Tetrahedron':
                add_tetrahedron(self)
            elif self.shape == 'Octahedron':
                add_octahedron(self)
            elif self.shape == 'Cone':
                add_cone(self)
            elif self.shape == 'Quad':
                add_quad(self)
            elif self.shape == 'Circle':
                add_circle(self)
            
            elif self.shape == 'Triangle':
                add_triangle(self)
            else:
                print(' Warning: ' , self.shape, ' Not Defined ')
                return
        else:
            if self.type == "Text":
                add_box(self)
            elif self.type == "Light":
                add_light(self)
            elif self.type == "Model":
                add_box(self)
            elif self.type == 'Sphere':
                if self.uv_sphere:
                   add_uv_sphere(self)
                else: 
                   add_sphere(self)

            else:
                print(' Warning: ' , self.type, self.shape, ' Not Supported ')
                return
            
            
        if self.blender_object.type == "MESH":
            for child in self.children:
                ## Merge Materials Here.
                for material in child.blender_object.data.materials.values():
                    
                    if material is not None and material not in bpy.context.object.data.materials.values():          
                        bpy.context.object.data.materials.append(material)
            
                if self.scene.use_boolean_operation is not 'NONE':
                    bpy.ops.object.modifier_add(type='BOOLEAN')
                    name = child.name + '-Boolean'
                    bpy.context.object.modifiers["Boolean"].name = name
                    bpy.context.object.modifiers[name].operation = 'UNION'
                    bpy.context.object.modifiers[name].solver = self.scene.use_boolean_operation
                    bpy.context.object.modifiers[name].object = child.blender_object
                    bpy.ops.object.modifier_apply(apply_as='DATA', modifier=name)
                    bpy.data.objects.remove(child.blender_object)
                        
                elif self.scene.join_children:
                    child.select()
                    self.select()
                    bpy.ops.object.join()

        self.select()
        
        if self.blender_object.type == "MESH":
            bpy.ops.object.modifier_add(type='EDGE_SPLIT')
            bpy.ops.object.mode_set(mode = 'EDIT')
            if len(self.children)>0:
                bpy.ops.mesh.remove_doubles(threshold=self.scene.merge_distance)
        
        bpy.ops.object.mode_set(mode = 'OBJECT')

        

    def relative_position(self):
        if self.parent is not None:
            position = self.parent.relative_position()
            return self.parent.relative_rotation() * self.position + position
        else:
            return self.position
        
                
    def relative_rotation(self):
        if self.parent is not None:
            rotation = self.parent.relative_rotation()
            return rotation * self.rotation
        else:
            return self.rotation
        
                

    def set_parent(self, parent):
        if type(parent) is HifiObject:
            self.parent = parent
        else:
            print('Warning: Type parent was not HifiObject')


    def add_child(self, child):
        self.children.append(child)
