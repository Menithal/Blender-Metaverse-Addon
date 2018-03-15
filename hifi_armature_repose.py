
import bpy
from mathutils import Quaternion, Matrix, Vector, Euler

from math import pi
from .hifi_armature_data import structure as base_armature


def fix_armature(obj):
    
    bpy.ops.object.mode_set(mode = 'OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    
    obj.select = True
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    obj.scale = Vector((100, 100, 100))
    
    print("Set Angle -90")
    str_angle = -90 * pi/180
    obj.rotation_euler = Euler((str_angle, 0, 0), 'XYZ')
    
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    
    obj.scale = Vector((0.01, 0.01, 0.01))
    obj.rotation_euler = Euler((-str_angle, 0, 0), 'XYZ')
    
    bpy.ops.object.select_all(action='DESELECT')


def navigate_armature(data, current_rest_node, world_matrix, parent, parent_node):

    name = current_rest_node["name"] 
    bone = data.get(name)
       
    if(bone):
        print(name)   
        bone.rotation_mode = "QUATERNION"
        
        destination_matrix = current_rest_node["matrix_local"].copy()
        inv_destination_matrix = destination_matrix.inverted()
        
        matrix = bone.matrix
        
        if parent:
            parent_matrix = parent.matrix.copy()
            parent_inverted = parent_matrix.inverted()
            parent_destination = parent_node["matrix_local"].copy()
        else:
            parent_matrix = Matrix()
            parent_inverted = Matrix()
            parent_destination = Matrix()
            
        smat = inv_destination_matrix * (parent_destination * ( parent_inverted * matrix))
            
        bone.rotation_quaternion = smat.to_quaternion().inverted()
             
        for child in current_rest_node["children"]:
        
            navigate_armature(data, child, world_matrix, bone, current_rest_node)

    else:
        bone = parent

        for child in current_rest_node["children"]:
            navigate_armature(data, child, world_matrix, bone, parent_node)
             

def retarget_armature(options):        
    
    obj = bpy.context.object
    if obj.type == "ARMATURE":
        print("Got Armature")
        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.select_all(action='SELECT')

        bpy.ops.pose.transforms_clear()
        bpy.ops.pose.select_all(action='DESELECT')
        print("---")
        world_matrix = obj.matrix_world
        bones = obj.pose.bones
        for bone in base_armature:
            navigate_armature(bones, bone, world_matrix, None, None) 
            print("Iterating Bones")
             
        bpy.ops.object.mode_set(mode='OBJECT')
        
        if options['apply']:
            
            print("Now Fix Armature for all")
            bpy.context.scene.objects.active = obj
            print(bpy.context.active_object.name)
            
            bpy.ops.object.mode_set(mode='POSE')           
            bpy.ops.pose.armature_apply()        
            bpy.ops.object.mode_set(mode='OBJECT')  
            fix_armature(obj)  

            for child in obj.children:
                armature = None

                for modifier in child.modifiers:
                    if modifier.type == "ARMATURE" and modifier.object == obj:       
                        name = modifier.name
                        ## COPY OTHER SETTINGs
                        print("Apply", name, " to ", child.name)

                        bpy.context.scene.objects.active = child
                        armature = modifier
                        bpy.ops.object.modifier_apply(apply_as='DATA', modifier=modifier.name)
                        break
                        
                # If Overriden Armature is found, then override
                if armature:
                    print("Creating new modifier", name, "_fix for ", child.name)
                    new_modifier = child.modifiers.new(name + "_fix", "ARMATURE")
                    new_modifier.object = obj

                print("Rescale", child.name, child.dimensions, child.scale)
                bpy.context.scene.objects.active = child
                ### TODO> Something is wrong here. its not scaling the parent correctly
                 # Then the scale correction assume current is correct
                child.select = True
                print('Active is', bpy.context.active_object.name, bpy.context.selected_objects)
                state = bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
                print(state)
                print("Now", child.name, child.dimensions, child.scale, bpy.context.selected_objects)
                child.scale = Vector((100, 100, 100))
                
                # Now Rescale to the correct one.
                bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
                
                print(bpy.context.active_object.name)
                print("Added size", child.name, child.dimensions, child.scale)
                child.scale = Vector((0.01, 0.01, 0.01))     
                child.select = False
                print("Down Scaled to Normal", child.name, child.dimensions, child.scale)
                

       

#retarget_armature({'apply': True})