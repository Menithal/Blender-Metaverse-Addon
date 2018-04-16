# -*- coding: utf-8 -*-

import csv
import bpy
import re
import os
from math import pi
from mathutils import Vector
# Based on powroupi the MMD Translation script combined with a Hogarth-MMD Translation csv that has been modified to select names as close as possible
# This instead uses a predefined list that is Hifi Compatable.

# Clone of shorthand to full
jp_half_to_full_tuples = (
    ('ｳﾞ', 'ヴ'), ('ｶﾞ', 'ガ'), ('ｷﾞ', 'ギ'), ('ｸﾞ', 'グ'), ('ｹﾞ', 'ゲ'),
    ('ｺﾞ', 'ゴ'), ('ｻﾞ', 'ザ'), ('ｼﾞ', 'ジ'), ('ｽﾞ', 'ズ'), ('ｾﾞ', 'ゼ'),
    ('ｿﾞ', 'ゾ'), ('ﾀﾞ', 'ダ'), ('ﾁﾞ', 'ヂ'), ('ﾂﾞ', 'ヅ'), ('ﾃﾞ', 'デ'),
    ('ﾄﾞ', 'ド'), ('ﾊﾞ', 'バ'), ('ﾊﾟ', 'パ'), ('ﾋﾞ', 'ビ'), ('ﾋﾟ', 'ピ'),
    ('ﾌﾞ', 'ブ'), ('ﾌﾟ', 'プ'), ('ﾍﾞ', 'ベ'), ('ﾍﾟ', 'ペ'), ('ﾎﾞ', 'ボ'),
    ('ﾎﾟ', 'ポ'), ('｡', '。'), ('｢', '「'), ('｣', '」'), ('､', '、'),
    ('･', '・'), ('ｦ', 'ヲ'), ('ｧ', 'ァ'), ('ｨ', 'ィ'), ('ｩ', 'ゥ'),
    ('ｪ', 'ェ'), ('ｫ', 'ォ'), ('ｬ', 'ャ'), ('ｭ', 'ュ'), ('ｮ', 'ョ'),
    ('ｯ', 'ッ'), ('ｰ', 'ー'), ('ｱ', 'ア'), ('ｲ', 'イ'), ('ｳ', 'ウ'),
    ('ｴ', 'エ'), ('ｵ', 'オ'), ('ｶ', 'カ'), ('ｷ', 'キ'), ('ｸ', 'ク'),
    ('ｹ', 'ケ'), ('ｺ', 'コ'), ('ｻ', 'サ'), ('ｼ', 'シ'), ('ｽ', 'ス'),
    ('ｾ', 'セ'), ('ｿ', 'ソ'), ('ﾀ', 'タ'), ('ﾁ', 'チ'), ('ﾂ', 'ツ'),
    ('ﾃ', 'テ'), ('ﾄ', 'ト'), ('ﾅ', 'ナ'), ('ﾆ', 'ニ'), ('ﾇ', 'ヌ'),
    ('ﾈ', 'ネ'), ('ﾉ', 'ノ'), ('ﾊ', 'ハ'), ('ﾋ', 'ヒ'), ('ﾌ', 'フ'),
    ('ﾍ', 'ヘ'), ('ﾎ', 'ホ'), ('ﾏ', 'マ'), ('ﾐ', 'ミ'), ('ﾑ', 'ム'),
    ('ﾒ', 'メ'), ('ﾓ', 'モ'), ('ﾔ', 'ヤ'), ('ﾕ', 'ユ'), ('ﾖ', 'ヨ'),
    ('ﾗ', 'ラ'), ('ﾘ', 'リ'), ('ﾙ', 'ル'), ('ﾚ', 'レ'), ('ﾛ', 'ロ'),
    ('ﾜ', 'ワ'), ('ﾝ', 'ン'),
)


bones_to_remove = [
    "Center",
    "Groove",
    "CenterTop",
    "ParentNode",
    "Eyes",
    "Dummy",
    "Root",
    "Base",
    "ControlNode"
]

contains_to_remove = [
    "_dummy_",
    "_shadow_",
    "IK",
    "Dummy",
    "Top",
    "Tip",
    "Twist",
    "ShoulderP",
    "ShoulderC",
    "LegD",
    "FootD",
    "mmd_edge",
    "mmd_vertex",
    "Node",
    "Center",
    "Control"
    
]

bones_to_correct = [
    "Arm",
    "LeftHand",
    "RightHand",
    "Finger",
    "Thumb",
    "Leg",
    "Foot",
    "Shoulder"
]

bones_to_correct_rolls = [
    135,
    215,
    -215,
    135,
    55,
    180,
    180,
    -180
]

parent_structure = {
    #Bone : Parent
    "LeftToe": "LeftFoot",
    "RightToe": "RightFoot",
    "LeftFoot": "LeftLeg",
    "RightFoot": "RightLeg",
    "LeftLeg": "LeftUpLeg",
    "RightLeg": "RightUpLeg",
    "LeftUpLeg": "Hips",
    "RightUpLeg": "Hips",
    "Spine1": "Spine",
    "Spine2": "Spine1",
    "Spine": "Hips",
    "Neck": "Spine2",
    "Head": "Neck",
    "LeftShoulder": "Spine2",
    "RightShoulder": "Spine2",
    "LeftArm": "LeftShoulder",
    "RightArm": "RightShoulder",
    "LeftForeArm": "LeftArm",
    "RightForeArm": "RightArm",
    "LeftHand": "LeftForeArm",
    "RightHand": "RightForeArm",
    "RightEye": "Head",
    "LeftEye": "Head"
}

# Simplified Translator based on powroupi MMDTranslation
class MMDTranslator:
    def __init__(self):
        self.translation_dict = []
        split_pattern = re.compile(",\s")
        remove_end = re.compile(",$")

        print(__file__)
        try:
            local = os.path.dirname(os.path.abspath(__file__))
            filename = os.path.join(local, 'mmd_hifi_dict.csv')
            with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
                try:
                    stream = csv.reader(
                        f, delimiter=',', quotechar='"', skipinitialspace=True)
                    self.translation_dict = [tuple(row)
                                             for row in stream if len(row) >= 2]
                finally:
                    f.close()
                    print("Translation File Loaded")
        except FileNotFoundError:  #Probably just developing then
            print("Reading Editor file: This only should show when developing")
            stream = bpy.data.texts["mmd_hifi_dict.csv"].lines
            for line in stream:
                body = line.body
                body = body.replace('"', '')
                body = re.sub(remove_end, "", body)
                
                tup = split_pattern.split(body)
                self.translation_dict.append( tuple(tup))
                
            print("Done Reading List")
            print("|||||||||||||||||||||||||||||||||||||||||")
                

    @staticmethod
    def replace_from_tuples(name, tuples):
        for pair in tuples:
            if pair[0] in name:
               updated_name = name.replace(pair[0], pair[1])
               name = updated_name
        return name

    def half_to_full(self, name):
        return self.replace_from_tuples(name, jp_half_to_full_tuples)

    def is_translated(self, name):
        try:
            name.encode('ascii', errors='strict')
        except UnicodeEncodeError:
            return False
        return True

    def translate(self, name):
        full_name = self.half_to_full(name)  # First Updates short hand to full
     
        translated_name = self.replace_from_tuples(full_name, self.translation_dict)
    
        return purge_string(translated_name)


def purge_string(string):
    try:
        str_bytes = os.fsencode(string)
        return str_bytes.decode("utf-8", "replace")
    except UnicodeEncodeError:
        print("Could not purge string", string)
        return string


def delete_self_and_children(me):
    
    print(bpy.context.mode)
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
        
    me.hide = False
    me.hide_select = False
    me.select = True
    bpy.context.scene.objects.active = me
    
    for child in me.children:
        child.hide = False
        child.hide_select = False
        child.select = True
    
    bpy.ops.object.delete()
    


#####################################################
# Armature Fixes:

def translate_bones(Translator, bones):
    for idx, bone in enumerate(bones):
        bone.hide = False
        bone.hide_select = False
        
        translated = Translator.translate(bone.name)
        bone.name = translated


def has_removable(val):
    for word in contains_to_remove:
        if word in val:
            return True
    return False

def correct_bone_parents(bones):
    
    keys = parent_structure.keys();
    
    for bone in bones:
        if bone.name == "Hips":
            bone.parent = None
        else:
            parent = parent_structure.get(bone.name)
            if parent is not None:
                parent_bone = bones.get(parent)
                if parent_bone is not None:
                    bone.parent = parent_bone
                

def correct_bone_rotations(obj):
    if "Eye" in obj.name:
        print("   ", obj.name)
        bone_head = Vector(obj.head)
        bone_head.z += 0.05
        obj.tail = bone_head
    elif "Hips" == obj.name:
        bone_head = Vector(obj.head)
        bone_tail = Vector(obj.tail)
        if bone_head.z > bone_tail.z:
            obj.head = bone_tail
            obj.tail = bone_head
        else:
            print("Hips already correct")
    else:
        for idx, name in enumerate(bones_to_correct):
            if name in obj.name:
                print("   Updating Roll of",obj.name, "with", bones_to_correct_rolls[idx], "current", obj.roll)
                obj.roll = bones_to_correct_rolls[idx] * (pi/180)
    
def clean_up_bones(obj):
    _to_remove = []
    
    pose_bones = obj.pose.bones

    bpy.ops.object.mode_set(mode='EDIT')  
    updated_context = bpy.data.objects[obj.name]
    edit_bones = updated_context.data.edit_bones
    
    bpy.ops.object.mode_set(mode='OBJECT')  
    for bone in obj.data.bones:
        pose_bone = pose_bones.get(bone.name)
        
        bpy.ops.object.mode_set(mode='EDIT')  # Oddly needed to get the edit bone reference
        edit_bone = edit_bones.get(bone.name)
     
        print(" Bone ", bone.name)
        
        
        if pose_bone is not None and edit_bone is not None:
            if has_removable(bone.name) or bone.name in bones_to_remove:
                if bone.name != "HeadTop" and edit_bone not in _to_remove: #There is an odd chance of duplicates, not sure why!
                    _to_remove.append(edit_bone)
                    print(" - Added to removal list", bone.name)
            else:
                print(" + Setting Pose Mode for", pose_bone)
                
                print(" - Removing Constraints from", pose_bone.name)
                for constraint in pose_bone.constraints:
                    pose_bone.constraints.remove(constraint)
                
                print(" # Check Rotations")
                correct_bone_rotations(edit_bone)
                    
                
            
    print(" Cleaning ", len(_to_remove), " unusable bones")
    
    for removal_bone in _to_remove:
        if removal_bone is not None:
            print(" Remove Bone:", removal_bone)
            edit_bones.remove(removal_bone)
            
            
    bpy.ops.object.mode_set(mode='EDIT')
    edit_bones = updated_context.data.edit_bones
    
    print("Manipulating", obj.name)
    if edit_bones.get("Spine1") is None:
        print("Couldnt Detect Spine1, Creating Out of Spine2")
        spine = edit_bones.get("Spine2")
        spine.select = True
        bpy.ops.armature.subdivide()
        spine.name = "Spine1"
        spine = edit_bones.get("Spine2.001")
        spine.name = "Spine2"
        
    
    edit_bones = updated_context.data.edit_bones
    correct_bone_parents(edit_bones)
    
    bpy.ops.object.mode_set(mode='OBJECT')  


def convert_bones(Translator, obj):
    bones = obj.data.bones
    
    print("Translating ", len(bones), " bones")
    # Translate Bones first. Have to do separate from the next loop
    translate_bones(Translator, bones)
    print("Cleaning Up Bones")
    clean_up_bones(obj)
    
        
def has_armature_as_child(me):
    for child in me.children:
        if child.type == "ARMATURE":
            return True
    return False


#####################################################
# Material Fixes

toon_override = re.compile("^((toon)|\w{1,2})\d*\.?\d*$")
def clean_textures(Translator, material):
    name = None
    
    for idx, texture_slot in enumerate(material.texture_slots):
        if texture_slot is not None and texture_slot.texture is not None:
            if toon_override.match(texture_slot.name):
                material.texture_slots.clear(idx)
            else:
                name = Translator.translate(texture_slot.name)
                texture_slot.texture.name = name
    
    return name
    
def merge_textures(unique_textures, materials_slots):
      
    for key in unique_textures.keys():
        print("Creating new material Texture")
        material_list = unique_textures[key]
        n = material_list.pop(0)
        first_material = materials_slots.get(n)
        
        print(first_material)
        root_material = key + "_material"
        first_material.material.name = root_material
        root_index = materials_slots.find(root_material)
        
        
        bpy.ops.object.mode_set(mode='EDIT')    
        
        if len(material_list) > 0:
            for material in material_list:
                index = materials_slots.find(material)
                if index > -1:
                    bpy.context.object.active_material_index = index
                    bpy.ops.object.material_slot_select()
        
        bpy.context.object.active_material_index = root_index
        bpy.ops.object.material_slot_select()
        bpy.ops.object.material_slot_assign()
        
        bpy.ops.object.mode_set(mode='OBJECT') 
        
        if len(material_list) > 0:
            for material in material_list:
                index = materials_slots.find(material)
                
                if index > -1:
                    bpy.context.object.active_material_index = index
                    bpy.ops.object.material_slot_remove()

def make_materials_fullbright(materials_slots):
	for material_slot in materials_slots:
		print(material_slot)
		material = material_slot.material
		material.specular_shader = 'WARDISO'
		material.use_shadeless = True
		material.specular_color = (0,0,0)
	

def clean_materials(Translator, materials_slots):
    
    _unique_textures = {}
    for material_slot in materials_slots:
        if material_slot is not None and material_slot.material is not None:
            material_slot.material.name = Translator.translate(material_slot.name)
            texture_name = clean_textures(Translator, material_slot.material)
            
            if texture_name is not None and _unique_textures.get(texture_name) is None:
                _unique_textures[texture_name] = [material_slot.material.name]
            elif texture_name is not None:
                _unique_textures[texture_name].append(material_slot.material.name)
    
    
    print("Found", len(_unique_textures.keys()), "unique textures from", len(materials_slots), "slots")
    
    merge_textures(_unique_textures, materials_slots)
    # make_materials_fullbright(materials_slots)

#####################################################
# Mesh Fixes:

def translate_shape_keys(Translator, shape_keys):
    print(" Translating shapekeys ", shape_keys.items())
    for key in shape_keys.items():
        print(key)
        shape_key = key[1]
        shape_key.name = Translator.translate(shape_key.name)
        
        if shape_key.name == "GoUp":
            shape_key.name = "BrowsU_C"
        elif shape_key.name == "GoDown":
            shape_key.name = "BrowsD_C"
            
            
def mix_weights(a,b):
    print("  Mixing",a,b)
    bpy.ops.object.modifier_add(type='VERTEX_WEIGHT_MIX')
    bpy.context.object.modifiers["VertexWeightMix"].vertex_group_a = a
    bpy.context.object.modifiers["VertexWeightMix"].vertex_group_b = b
    bpy.context.object.modifiers["VertexWeightMix"].mix_mode = 'ADD'

    bpy.context.object.modifiers["VertexWeightMix"].mix_set = 'OR'
    bpy.ops.object.modifier_apply(apply_as='DATA', modifier="VertexWeightMix")
    
    
def fix_vertex_groups(obj):
    vertex_groups = obj.vertex_groups
    arm_re = re.compile("ArmTwist\d?$")
    hand_re = re.compile("HandTwist\d?$")
    
    shoulder_re = re.compile("ShoulderP|C$")
    leg_re = re.compile("LegD$")
    foot_re = re.compile("FootD$")
    
    remove_list = []
    for vertex_group in vertex_groups:
        if "IK" in vertex_group.name:
            remove_list.append(vertex_group.name)
            
        if "ArmTwist" in vertex_group.name:
            root = re.sub(arm_re, "Arm", vertex_group.name)
            parent = vertex_groups.get(root)
            if parent is not None:
                mix_weights(root, vertex_group.name)
                remove_list.append(vertex_group.name)
                
        elif re.search(shoulder_re, vertex_group.name) != None:
            root = re.sub(shoulder_re, "Shoulder", vertex_group.name)
            parent = vertex_groups.get(root)
            if parent is not None:
                mix_weights(root, vertex_group.name)
                remove_list.append(vertex_group.name)
        elif re.search(leg_re, vertex_group.name) != None:
            root = re.sub(leg_re, "Leg", vertex_group.name)
            parent = vertex_groups.get(root)
            if parent is not None:
                mix_weights(root, vertex_group.name)
                remove_list.append(vertex_group.name)
        
        elif re.search(foot_re, vertex_group.name) != None:
            root = re.sub(foot_re, "Foot", vertex_group.name)
            parent = vertex_groups.get(root)
            if parent is not None:
                mix_weights(root, vertex_group.name)
                remove_list.append(vertex_group.name)
                
        elif "HandTwist" in vertex_group.name:
            root = re.sub(hand_re, "ForeArm", vertex_group.name)
            parent = vertex_groups.get(root)
            if parent is not None:
                mix_weights(root, vertex_group.name)
                remove_list.append(vertex_group.name)
    
    print("  Cleaning Unused vertex groups")
    for group in remove_list:
        print("Removing VertexGroups", group)
        vertex_groups.remove(vertex_groups.get(group))

def clean_mesh(Translator, obj):
    bpy.ops.object.mode_set(mode='OBJECT')  
    print(" Converting",obj.name,"Mesh")
    translate_shape_keys(Translator, obj.data.shape_keys.key_blocks)
    fix_vertex_groups(obj)

#### --------------------

def parse_mmd_avatar_hifi():
    # Should Probably have a confirmation dialog when using this.
    original_type = bpy.context.area.type
    bpy.context.area.type = 'VIEW_3D'

    Translator = MMDTranslator()
    # Change mode to object mode
    
    marked_for_purge = []
    marked_for_deletion = []
    
    bpy.ops.object.mode_set(mode='OBJECT')  

    for scene in bpy.data.scenes:
        for obj in scene.objects:
            bpy.ops.object.select_all(action='DESELECT')
            if obj is not None:
                obj.select = True
                bpy.context.scene.objects.active = obj
                # Delete joints and rigid bodies items. Perhaps later convert this to flow.
                print("Reading", obj.name)
                if obj.name == "joints" or obj.name == "rigidbodies":
                    marked_for_purge.append(obj)
                elif obj.type == "EMPTY" and obj.parent is None: 
                    marked_for_deletion.append(obj)
                
                elif obj.type == 'ARMATURE':
                    print(obj.name, obj.type)
                    convert_bones(Translator, obj)
                    
                elif obj.type == 'MESH' and obj.parent is not None and obj.parent.type == 'ARMATURE':
                    clean_mesh(Translator, obj)
                    bpy.ops.object.mode_set(mode='OBJECT')  
                    clean_materials(Translator, obj.material_slots)
                    
            # translate armature names!
    
    bpy.ops.object.select_all(action='DESELECT')
    for deletion in marked_for_deletion:
        deletion.select = True
        bpy.context.scene.objects.active = deletion
        bpy.ops.object.delete()
    
    bpy.ops.object.select_all(action='DESELECT')
    for deletion in marked_for_purge:
        delete_self_and_children(deletion)
            
    bpy.context.area.type = original_type