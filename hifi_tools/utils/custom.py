import bpy
import re
from hifi_tools.utils import bones, mesh, materials
from bpy.props import StringProperty, BoolProperty, PointerProperty


def poll(self, object):
    return object.type == "BONE"


def get_armatures(self, context):
    obj = []

    count = 0
    for ob in context.scene.objects:
        if ob.type == 'ARMATURE':
            # (key, label, descr, id, icon)
            # [(identifier, name, description, icon, number)
            obj.append((ob.name, ob.name, "ARMATURE_DATA"))
            count += 1

    return obj


def get_bones(self, context):

    armature = context.scene.objects.get(self.custom_armatures)

    print("--- get bones", armature)
    if armature is None:
        return
    return [(bone.name, bone.name, "") for bone in armature.data.bones]


hips_names = ["hips", "pelvis"]

neck_names = ["neck", "collar"]

shoulder_names = ["clavicle", "shoulder"]

foot_name = "foot"
toe_name = "toe"

hand_name = "hand"

hand_re = re.compile("hand$")

hand_thumb_name = "thumb1"
hand_index_name = "index1"
hand_middle_name = "middle1"
hand_ring_name = "ring1"
hand_pinky_name = "pinky1"

spine_name = "spine"
spine1_name = "spine1"
head_name = "head"
eye_name = "eye"


def automatic_bind_bones(self, avatar_bones):
    print('------')

    for bone in avatar_bones:
        cleaned_name = bones.clean_up_bone_name(bone.name).lower()

        for hip_bone in hips_names:
            if hip_bone in cleaned_name:
                self.hips = bone.name

        if "spine2" in cleaned_name or "chest" in cleaned_name or "breast" in cleaned_name:
            self.spine2 = bone.name
        elif spine1_name in cleaned_name:
            self.spine1 = bone.name
        elif spine_name in cleaned_name:
            self.spine = bone.name

        for neck_bone in neck_names:
            if neck_bone in cleaned_name:
                self.neck = bone.name

        if "lowerarm" in cleaned_name or "forearm" in cleaned_name:
            self.fore_arm = bone.name
        elif "arm" in cleaned_name or "upperarm" in cleaned_name:
            self.arm = bone.name

        for shoulder_bone in shoulder_names:
            if shoulder_bone in cleaned_name:
                self.shoulder = bone.name

        if "upleg" in cleaned_name or "thigh" in cleaned_name or "upleg" in cleaned_name:
            self.up_leg = bone.name
        elif "calf" in cleaned_name or "leg" in cleaned_name:
            self.leg = bone.name

        if foot_name in cleaned_name:
            self.foot = bone.name

        if toe_name in cleaned_name:
            self.toe = bone.name

        if hand_thumb_name in cleaned_name:
            self.hand_thumb = bone.name

        elif hand_index_name in cleaned_name:
            self.hand_index = bone.name

        elif hand_middle_name in cleaned_name:
            self.hand_middle = bone.name

        elif hand_ring_name in cleaned_name:
            self.hand_ring = bone.name

        elif hand_pinky_name in cleaned_name:
            self.hand_pinky = bone.name

        elif hand_re.search(cleaned_name) is not None:
            self.hand = bone.name

        if head_name in cleaned_name:
            self.head = bone.name

        if eye_name in cleaned_name:
            self.eye = bone.name


def update_bone_name(edit_bones, from_name, to_name):
    bone_to_edit = edit_bones.get(from_name)
    if bone_to_edit is not None:
        print("Converting", from_name, "to", to_name)
        bone_to_edit.name = to_name


def update_bone_name_mirrored(edit_bones, from_name, to_name):
    mirrored = bones.get_bone_side_and_mirrored(from_name)
    if mirrored is not None:
        update_bone_name(edit_bones, from_name, mirrored.side + to_name)
        update_bone_name(edit_bones, mirrored.mirror_name,
                         mirrored.mirror + to_name)


def update_bone_name_chained_mirrored(edit_bones, from_name, to_name):
    bone = bones.get_bone_side_and_mirrored(from_name)
    if bone.index is not None:
        update_bone_name_mirrored(edit_bones, from_name, to_name + bone.index)
        ebone = edit_bones[bone.name]
        next_index = str(int(bone.index)+1)
        if ebone is not None and len(ebone.children) > 0 and bone.index is not None:
            update_bone_name_chained_mirrored(edit_bones, from_name.replace(
                bone.index, next_index), to_name)


def rename_bones_and_fix_most_things(self, context):
    print("Rename bones fix most things", self.armatures)
    if len(self.armatures) < 1:
        print("Armature Update cancelled")
        return {"CANCELLED"}

    # Naming Converted
    bpy.ops.object.mode_set(mode="EDIT")
    print("Armatures")
    armature = bpy.data.armatures[self.armatures]
    ebones = armature.edit_bones

    print("Updating Bone Names")
    update_bone_name(ebones, self.hips, "Hips")
    update_bone_name(ebones, self.spine, "Spine")
    update_bone_name(ebones, self.spine1, "Spine1")
    update_bone_name(ebones, self.spine2, "Spine2")
    update_bone_name(ebones, self.neck, "Neck")
    update_bone_name(ebones, self.head, "Head")

    print("Updating Bone Names Mirrored")
    update_bone_name_mirrored(ebones, self.eye, "Eye")
    update_bone_name_mirrored(ebones, self.shoulder, "Shoulder")
    update_bone_name_mirrored(ebones, self.arm, "Arm")
    update_bone_name_mirrored(ebones, self.fore_arm, "ForeArm")
    update_bone_name_mirrored(ebones, self.hand, "Hand")

    update_bone_name_mirrored(ebones, self.up_leg, "UpLeg")
    update_bone_name_mirrored(ebones, self.leg, "Leg")
    update_bone_name_mirrored(ebones, self.foot, "Foot")
    update_bone_name_mirrored(ebones, self.toe, "Toe")

    print("Updating Bone Names Chained Mirrored")
    update_bone_name_chained_mirrored(ebones, self.hand_thumb, "HandThumb")
    update_bone_name_chained_mirrored(ebones, self.hand_index, "HandIndex")
    update_bone_name_chained_mirrored(ebones, self.hand_middle, "HandMiddle")
    update_bone_name_chained_mirrored(ebones, self.hand_ring, "HandRing")
    update_bone_name_chained_mirrored(ebones, self.hand_pinky, "HandPinky")

    # Fixing Rotations and Scales
    for bone in ebones:
        bones.correct_bone_rotations(bone)
        bones.correct_bone(bone, ebones)
    
    bones.correct_bone_parents(armature.edit_bones)

    bpy.ops.object.mode_set(mode="OBJECT")
    
    bpy.ops.object.select_all(action="DESELECT")
    children = bpy.data.objects

    for child in children:    
        if child.type == "ARMATURE":
            
            child.select = True
    
            bones.correct_scale_rotation(child, True)
            bones.correct_bone_rotations(child)
            bpy.ops.object.mode_set(mode="POSE")
            bpy.ops.pose.select_all(action="SELECT")
            bpy.ops.pose.transforms_clear()
            bpy.ops.pose.select_all(action="DESELECT")
            bpy.ops.object.mode_set(mode="OBJECT")
        if child.type == "MESH":
    #        mesh.clean_unused_vertex_groups(child)
            materials.clean_materials(child.material_slots)

    for material in bpy.data.materials:
        materials.flip_material_specular(material)

    bpy.ops.object.mode_set(mode="OBJECT")
 
    return {"FINISHED"}


class HifiCustomAvatarBinderOperator(bpy.types.Operator):
    bl_idname = "hifi.mirror_custom_avatar_bind"
    bl_label = "Custom Avatar Binding Tool"

    custom_armature_name = bpy.props.StringProperty()
    armatures = bpy.props.EnumProperty(
        name="Select Armature", items=get_armatures)

    hips = bpy.props.StringProperty()
    spine = bpy.props.StringProperty()
    spine1 = bpy.props.StringProperty()
    spine2 = bpy.props.StringProperty()
    neck = bpy.props.StringProperty()
    head = bpy.props.StringProperty()
    # Head
    eye = bpy.props.StringProperty()
    head_top = bpy.props.StringProperty()
    # Arms
    # right
    shoulder = bpy.props.StringProperty()
    arm = bpy.props.StringProperty()
    fore_arm = bpy.props.StringProperty()
    hand = bpy.props.StringProperty()

    # Fingers
    hand_thumb = bpy.props.StringProperty()
    hand_index = bpy.props.StringProperty()
    hand_middle = bpy.props.StringProperty()
    hand_ring = bpy.props.StringProperty()
    hand_pinky = bpy.props.StringProperty()
    # Legs
    up_leg = bpy.props.StringProperty()
    leg = bpy.props.StringProperty()
    foot = bpy.props.StringProperty()
    toe = bpy.props.StringProperty()

    def execute(self, context):
        return rename_bones_and_fix_most_things(self, context)

    def invoke(self, context, event):
        if self.armatures:
            data = context.scene.objects[self.armatures].data
            automatic_bind_bones(self, data.bones)
            # self.hips = "Hips"

        return context.window_manager.invoke_props_dialog(self, width=600)

    def draw(self, context):
        layout = self.layout
        layout.label("This is an Experimental Feature. Please comment in the forums if there are any issues with rebinding.")
        layout.label("Everything is mirrored.")
        column = layout.column()

       # column.prop_search(scene, "custom_current_armature", bpy.data, "armatures", icon='ARMATURE_DATA', text="Select Armature")
        column.prop(self, "armatures")
        # context.scene.object[self.armatures]

        if self.armatures is not "":
            data = context.scene.objects[self.armatures].data

            # Do Filtering of the data set

            column.prop_search(self, 'hips', data, 'bones',
                               icon='BONE_DATA', text='Hips')
            column.prop_search(self, 'spine', data, 'bones',
                               icon='BONE_DATA', text='Spine')
            column.prop_search(self, 'spine1', data, 'bones',
                               icon='BONE_DATA', text='Spine Additional*')
            column.prop_search(self, 'spine2', data, 'bones',
                               icon='BONE_DATA', text='Chest')
            column.prop_search(self, 'neck', data, 'bones',
                               icon='BONE_DATA', text='Neck')
            column.prop_search(self, 'head', data, 'bones',
                               icon='BONE_DATA', text='Head')

            # Head
            column.prop_search(self, 'eye', data, 'bones',
                               icon='BONE_DATA', text='Left Eye')

            column.prop_search(self, 'head_top', data, 'bones',
                               icon='BONE_DATA', text='Head Top')
            # Arms
            column.prop_search(self, 'shoulder', data, 'bones',
                               icon='BONE_DATA', text='Shoulder')
            column.prop_search(self, 'arm', data, 'bones',
                               icon='BONE_DATA', text='Arm')
            column.prop_search(self, 'fore_arm', data, 'bones',
                               icon='BONE_DATA', text='ForeArm')
            column.prop_search(self, 'hand', data, 'bones',
                               icon='BONE_DATA', text='Hand')

            column.prop_search(self, 'hand_thumb', data,
                               'bones', icon='BONE_DATA', text='Thumb 1st')
            column.prop_search(self, 'hand_index', data, 'bones',
                               icon='BONE_DATA', text='Index Finger 1st')
            column.prop_search(self, 'hand_middle', data, 'bones',
                               icon='BONE_DATA', text='Middle Finger 1st')
            column.prop_search(self, 'hand_ring', data, 'bones',
                               icon='BONE_DATA', text='Ring Finger 1st')
            column.prop_search(self, 'hand_pinky', data,
                               'bones', icon='BONE_DATA', text='Pinky 1st')

            # Legs
            column.prop_search(self, 'up_leg', data, 'bones',
                               icon='BONE_DATA', text='Thigh')
            column.prop_search(self, 'leg', data, 'bones',
                               icon='BONE_DATA', text='Leg')
            column.prop_search(self, 'foot', data, 'bones',
                               icon='BONE_DATA', text='Foot')
            column.prop_search(self, 'toe', data, 'bones',
                               icon='BONE_DATA', text='Toe')

        else:
            print(" No Armatures")

        print("custom_armature_name", self.custom_armature_name)
        # After selecting armature, iterate through bones.

# https://blender.stackexchange.com/questions/19293/prop-search-armature-bones


def scene_define():
    bpy.types.Scene.custom_armature_name = bpy.props.StringProperty()

    bpy.types.Scene.custom_armature_collection = bpy.props.CollectionProperty(
        type=bpy.types.PropertyGroup)


def scene_delete():
    del bpy.types.Scene.custom_armature_collection
    del bpy.types.Scene.custom_armature_name


def custom_register():
    bpy.utils.register_class(HifiCustomAvatarBinderOperator)


def custom_unregister():
    bpy.utils.unregister_class(HifiCustomAvatarBinderOperator)
