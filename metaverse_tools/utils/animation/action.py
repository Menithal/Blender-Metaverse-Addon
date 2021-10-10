import math
import bpy
from typing import Dict
from metaverse_tools.utils.bones.bones_builder import mirrorable_name_re, get_bone_side_and_mirrored, BoneMirrorableInfo

from mathutils import Matrix, Vector, Euler, Quaternion
short_sides = ["L", "R"]
long_sides = ["Left", "Right"]

# TODO: This should be a universal naming schema. Figure out a place to move this to

class ObjectInfo:
    
    def __init__(self, location, rotation, rotation_mode, scale):
        # Make sure to clone instead of reference.
        self.location = Vector(location) 
        self.rotation_mode = rotation_mode
        
        if(self.rotation_mode in "QUATERNION"):
            self.rotation_euler = None
            self.rotation_quaternion = Quaternion(rotation)
        else:
            self.rotation_euler = Euler((rotation[0], rotation[1], rotation[2]), rotation_mode)
            self.rotation_quaternion = None

        self.scale = Vector(scale)

    def set_info_to_object(self, entity):
        entity.location = self.location
        if(self.rotation_mode in "QUATERNION"):
            entity.rotation_quaternion = self.rotation_quaternion
        else:
            entity.rotation_euler = self.rotation_euler
        entity.scale = self.scale


    def half(self):
        half_rotation = None
        if(self.rotation_mode != "QUATERNION"):
            half_rotation = self.rotation_quaternion.slerp(Quaternion(), 0.5)
        else:
            half_rotation = Euler((self.rotation_euler.x / 2, self.rotation_euler.y / 2, self.rotation_euler.z / 2), self.rotation_mode)
       
        return ObjectInfo(self.location / 2, half_rotation, self.rotation_mode, self.scale)


class BoneData:
    def __init__(self, name, frames):
        self.name = name
        self.frames = frames
        self.info: [ObjectInfo] = [None] * len(frames)
        self.mirrorable: BoneMirrorableInfo = get_bone_side_and_mirrored(name)

    def get_frames(self):
        return self.frames

    def len(self):
        return len(self.frames)

    def get_object_info(self, frame):
        if self.frames.get(frame) == None:
            return None

        ind = self.frames.index(frame)

        return self.info[ind]

    def set_object_info(self, frame, info: ObjectInfo):
        ind = self.frames.index(frame)
        self.info[ind] = info

    def get_info(self):
        return self.info

    def frame_info_tuple(self) -> [(int, ObjectInfo)]:
        info_frame = []
        for frame in self.frames:
            ind = self.frames.index(frame)
            info_frame.append((frame, self.info[ind]))
        return info_frame


def return_sides(name):
    if (name.find("**") != -1):
        return long_sides
    if (name.find("*") != -1):
        return short_sides
    
    return None

def get_max_frames_in_action(armature, action):
    active_bones_actions = action.groups
    max_frame = 0
    armature.animation_data.action = action
    for bone in active_bones_actions:
        for channel in bone.channels:
            for keyframe in channel.sampled_points.data.keyframe_points:
                x, y = keyframe.co
                if x > max_frame:
                    max_frame = x
    
    return max_frame
    

def get_bone_frames_in_action(armature, action):
    active_bones_actions = action.groups
    action_bones_dict: Dict[str, BoneData] = dict()

    armature.animation_data.action = action
    for bone in active_bones_actions:
        name = bone.name
        keyframes = []
        for channel in bone.channels:
            for keyframe in channel.sampled_points.data.keyframe_points:
                x, y = keyframe.co
                if x not in keyframes:
                    keyframes.append((math.ceil(x)))
        action_bones_dict[name] = BoneData(name, keyframes)
        for frame in keyframes:
            bpy.context.scene.frame_set(frame)
            pose_bone = armature.pose.bones[name]
            if "QUATERNION" in pose_bone.rotation_mode:
                info = ObjectInfo(pose_bone.location, pose_bone.rotation_quaternion, pose_bone.rotation_mode, pose_bone.scale)
            else:
                info = ObjectInfo(pose_bone.location, pose_bone.rotation_euler, pose_bone.rotation_mode, pose_bone.scale)
            
            action_bones_dict[name].set_object_info(frame, info)
            
    pose_bones = []
    # Convert Dict into a List
    for index in action_bones_dict:
        pose_bones.append(action_bones_dict[index])

    return pose_bones


def create_keyframe(pose_bone, frame, info):
    info.set_info_to_object(pose_bone)
    pose_bone.keyframe_insert('location', group=pose_bone.name, frame=frame)
   
    if "QUATERNION" in pose_bone.rotation_mode:   
        pose_bone.keyframe_insert('rotation_quaternion', group=pose_bone.name, frame=frame)
    else:   
        pose_bone.keyframe_insert('rotation_euler', group=pose_bone.name, frame=frame)

    pose_bone.keyframe_insert('scale', group=pose_bone.name, frame=frame)


def split_bone_frames_into_mirrored_action(armature, action, half = False):
    
    bpy.context.scene.tool_settings.use_keyframe_insert_auto = False
    name = action.name
    sides = return_sides(name)

    if sides is None: 
        print("Not mirrorable, skipping " + name)
        return

    split_action_name = mirrorable_name_re.split(name)
    keyframed_bones: [BoneData] = get_bone_frames_in_action(armature, action)

    def check_side (side, short_side, long_side, bone_side): 
        return (side == short_side or side == long_side) and long_side == bone_side

    for side in sides:
        action_name = split_action_name[0] + side + split_action_name[1]
        # Does Action exist? delete, then Generate New Action
        action_to_make = bpy.data.actions.get(action_name)

        if action_to_make != None:
            bpy.data.actions.remove(action_to_make)

        # Can now create a new action
        new_action = bpy.data.actions.new(action_name)
        armature.animation_data.action = new_action
        # Now have the action set, lets do some stuff with it.

        for bone in keyframed_bones:
            # If bone is mirrorable.
            pose_bone = armature.pose.bones[bone.name]

            if bone.mirrorable != None:
                if (check_side(side, 'R', 'Right', bone.mirrorable.side) or check_side(side, 'L', 'Left', bone.mirrorable.side)):
                    for frame, info in bone.frame_info_tuple():
                        create_keyframe(pose_bone, frame, info)
            else:
                for frame, info in bone.frame_info_tuple():
                    if half:
                        create_keyframe(pose_bone, frame, info.half())
                    else:
                        create_keyframe(pose_bone, frame, info)
                    # TODO: If its not a mirrorable, perhaps half the amount the animation is moving stuff, since its split?
 

def split_all_actions(armature, actions):
    for action in actions:
        split_bone_frames_into_mirrored_action(armature, action)
    
