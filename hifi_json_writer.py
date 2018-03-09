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

# Scene Logic for Exporting Blender Scenes
# By Matti 'Menithal' Lahtinen



import bpy
from .hifi_utility import *
import uuid
import re
import os
import json

from bpy.props import StringProperty
from mathutils import Quaternion
from math import sqrt

from bpy_extras.io_utils import ExportHelper
from hashlib import md5


EXPORT_VERSION = 84

def center_all(blender_object):
    for child in blender_object.children:
        select(child)
                
    blender_object.select = True
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    
    blender_object.select = False   


def select(blender_object):
    for child in blender_object.children:
        select(child)            
                
    blender_object.select = True
    

def parse_object(blender_object, path, options):  
    
    name = re.sub(r'\.\d{3}$', '', blender_object.name)
    # If you ahve an object thats the same mesh, but different object: All Objects will use this as reference allowing for instancing.
    mesh_name = blender_object.data.name
    uuid_gen = uuid.uuid5(uuid.NAMESPACE_DNS, blender_object.name)
    scene_id = str(uuid_gen)
    
    type = blender_object.type
    orientation = quat_swap_nzy(blender_object.rotation_quaternion)
    position = swap_nzy(blender_object.location)
    
    
    bpy.ops.object.select_all(action = 'DESELECT')
    if type == 'MESH':        
        blender_object.select = True
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
        
        dimensions = swap_yz(blender_object.dimensions)
        
        bpy.ops.export_scene.fbx(filepath=path + mesh_name + ".fbx", version='BIN7400', embed_textures=True, path_mode='COPY',
                                use_selection=True, axis_forward='-Z', axis_up='Y')
                                
        json_data = {
            'name': name,
            'id': scene_id,
            'type': 'Model',
            'modelURL': options['url'] + mesh_name + '.fbx',
            'position': {
                'x': position.x,
                'y': position.y,
                'z': position.z
            },
            'rotation': {
                'x': orientation.x,
                'y': orientation.y,
                'z': orientation.z,
                'w': orientation.w
            },
            'dimensions':{
                'x': dimensions.x,
                'y': dimensions.y,
                'z': dimensions.z
            },
            'userData': '{"blender_export":"' + scene_id +'"}'
        }         
        
        ## This gets quite Complex, as Id have to do this recursively.               
        if blender_object.parent:
            parent = blender_object.parent
            
            parent_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, parent.name)
            
            parent_orientation = quat_swap_nzy(relative_rotation(blender_object))
            parent_position = swap_nzy(relative_position(blender_object))
            
            json_data["position"] = {
                'x': parent_position.x,
                'y': parent_position.y,
                'z': parent_position.z
            }
            
            json_data["rotation"] = {
                'x': parent_orientation.x,
                'y': parent_orientation.y,
                'z': parent_orientation.z,
                'w': parent_orientation.w
            }
            
            json_data["parentID"] = str(parent_uuid)
            
            
        return json_data
            
    elif type == 'LAMP':
        print(name, 'is Light')
        
        # Hifi 5, Blender 3.3
        light = blender_object.data
        color = blender_object.color
        falloff = sqrt(light.distance)
        distance = light.distance
        
        json_data = {
            'name': name,
            'id': scene_id,
            'type': 'Light',
            'modelURL': options['url'] + mesh_name + '.fbx',
            'position': {
                'x': position.x,
                'y': position.y,
                'z': position.z
            },
            'color':{
                'blue': color[2],
                'green': color[1],
                'red': color[0]
            },
            'dimensions':{
                'x':distance,
                'y':distance,
                'z':distance,
            },
            'falloffRadius': falloff,
            'rotation': {
                'x': orientation.x,
                'y': orientation.y,
                'z': orientation.z,
                'w': orientation.w
            },

            'intensity': light.energy,
            'userData': '{"blender_export":"' + scene_id +'"}'
        }   
            
        if light.type is 'POINT':
            blender_object.select = True
            return json_data        
        
        # TODO: Spot Lights require rotation by 90 degrees to get pointing in the right direction
        return None
        
    elif type == 'ARMATURE': # Same as Mesh actually.
        print(name, 'is armature')
    
    else:
        print('Skipping unsupported feature', name, type)
    
        
    bpy.ops.object.select_all(action = 'DESELECT')

# Rotation is based on the rotaiton of the parent and self. 
def relative_rotation(parent_object):
    if not parent_object.parent:
        return parent_object.rotation_quaternion
    else:
        rotation = relative_rotation( parent_object.parent)
        current = parent_object.rotation_quaternion
        current.invert() 
        print('rotation test', current)
       
        return rotation * current


def relative_position(parent_object):
    if parent_object.parent is not None:
        return relative_rotation(parent_object.parent) * parent_object.location - relative_position(parent_object.parent)
    else:
        return parent_object.location


class HifiJsonWriter(bpy.types.Operator, ExportHelper):
    bl_idname ="export_scene.hifi_fbx_json"
    bl_label = "Export HiFi Scene"
    bl_options = {'UNDO'}
    
    directory = StringProperty()
    filename_ext = ".hifi.json"
    filter_glob = StringProperty(default="*.hifi.json", options={'HIDDEN'})
    
    url_override = StringProperty(default="", name="Marketplace / Base Url", 
                                    description="Set Marketplace / URL Path here to override")
    
    def draw(self, context):
        layout = self.layout
        layout.label("Url Override: Add Marketplace / URL to make sure that the content can be reached.")
        layout.prop(self, "url_override")
        

    def execute(self, context):
        if not self.filepath:
            raise Exception("filepath not set")
            
        if not self.url_override:
            raise Exception("Set the Marketplace / URL to make sure that the content can be reached.")
        
        current_scene = bpy.context.scene
        # Creating a temp copy to do the changes in.
        test = bpy.ops.scene.new(type='FULL_COPY')

        new_scene = bpy.context.scene
        new_scene.name = 'Hifi_Export_Scene'

        # Clone Scene. Then select scene. After done delete scene
        path = os.path.dirname(os.path.realpath(self.filepath)) + '/'
        
        ## Parse the marketplace url
        
        url = self.url_override
        if "https://highfidelity.com/marketplace/items/" in url:
            
            marketplace_id = url.replace("https://highfidelity.com/marketplace/items/", "").replace("/edit","").replace("/","")
            
            url = "http://mpassets.highfidelity.com/" + marketplace_id + "-v1/"
        
        if not url.endswith('/'):    
            url = url + "/"
        
        entities = []
        
        for blender_object in new_scene.objects:
            
            parsed = parse_object(blender_object, path, {'url': url})
            
            if parsed:
                entities.append(parsed)        
            

        bpy.ops.scene.delete()
        hifi_scene = {
            'Version': EXPORT_VERSION,
            'Entities': entities
        }
        
        data = json.dumps(hifi_scene, indent=4)
        
        file = open(self.filepath, "w")
        
        try: 
            file.write(data)
        except e:
            print('Could not write to file.', e)
        finally:
            file.close()
        
        return {'FINISHED'}
        
