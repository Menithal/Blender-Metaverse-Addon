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
# Copyright 2020 Matti 'Menithal' Lahtinen

from metaverse_tools.utils.facerig.models import FaceRigAnimationSet, FaceRigAnimationSetFlags, FaceRigAnimationSetFrames
import re
import enum
from metaverse_tools.utils.bones.bones_builder import mirrorable_name_re
from metaverse_tools.utils.animation.action import return_sides
from metaverse_tools.utils.facerig.models import *

required_bones = [
    "BipHead",
    "Camera",
    "BipLEye",
    "BipREye"
]

physics_bone_parent = "_planeNormal" # Normal should point outwards

### Shaders

SHADER_DOUBLE_SIDED_NORMALS = "_cull_none"
SHADER_BLENDING = "_blend1"
SHADER_MASK = "_blend2"

### Textures
# bitmaps .tga

texture_diffuse_suffix = "d"
texture_normal_map_suffix = "b"
texture_normal_map_additional_1_suffix = "b1"
texture_normal_map_additional_2_suffix = "b2"
texture_normal_map_additional_3_suffix = "b3"
texture_normal_map_additional_4_suffix = "b4"
# R => Glossiness factor, 
# G => Material values
# B => Emissive
# A => Specular Power
texture_specular_map_suffix = "s" 
texture_specular_map_additional_suffix = "s2"
texture_skin_scatter_suffix = "sc"

# R: PPAO for tensed muscles
# G: Relaxed Muscle 
# B: Tensed Muscles
texture_ambient_occlusion_suffix = "oc"
# R: skin specular behavior: 255 -> like short fur or hair. 0 -> normal specular
# G: Fur or hair transparency: 255 for full fur/hair, 0 for no fur/hair
# B: Skin specular intensity 0: no specular on skin (covered by fur) , 255: full specularity
texture_fur_mask_suffix = "m"
# Can have two separate color masks setup
texture_color_mask_suffix = "cm"

DEFAULT_MATERIAL_SHADER = "sht_skinoan"

valid_shader_names = ""



MIRRORED = FaceRigAnimationSetFlags(True)
DEFAULT_FLAGS = FaceRigAnimationSetFlags()
IDLE_ROOT = FaceRigAnimationSetFrames(0)



def set_to_list(animation_set_list: [FaceRigAnimationSet]):
    animation_names = []
    for animation_set in animation_set_list:
        name = animation_set.name
        if(animation_set.options.mirrorable):
            s = mirrorable_name_re.split(name)
            for side in return_sides(name):
                animation_names.append(s[0] + side + s[1])
        else:
            animation_names.append(name)

    return animation_names


# generalMovement
general_movement_directory = "generalMovement"
general_movement = [
    FaceRigAnimationSet("Avatar_FB"), # Avatar Leans Forward at 0, idle at 15, Backwards at 30
    FaceRigAnimationSet("Avatar_LR"), # Avatar Leans Left at 0, idle at 15, Right at 30
    FaceRigAnimationSet("Avatar_Twist"), # Avatar Leans Left at 0, idle at 15, Right at 30
    FaceRigAnimationSet("Head_LR"), # Head Leans Left at 0, idle at 15, Right at 30
    FaceRigAnimationSet("Head_Twist"), # Head Twists to left at 0,  idle at 15, Right at 30
    FaceRigAnimationSet("Head_UD"), # Head Looks up at 0, idle at 15, look down 30
    FaceRigAnimationSet("idle1") # idle Neutral position at 0, Can contain subtle movements.
]

general_movement_names = set_to_list(general_movement)
# EyesAndEyebrows
eye_and_eyebrows_directory = "EyesAndEyebrows"
eye_and_eyebrows = [
    FaceRigAnimationSet("**Eye_LR", MIRRORED), # Eye looks left at 0, idle at 15, right at 30
    FaceRigAnimationSet("**Eye_UD", MIRRORED), # Eye looks up at 0, idle at 15, down at 30
    FaceRigAnimationSet("**Eyebrow_D", FaceRigAnimationSetFlags(True, "_frown")), # Inner Half eyebrow down, frown like
    FaceRigAnimationSet("**Eyebrow_D_ext", MIRRORED), # Outer Half eyebrow down
    FaceRigAnimationSet("**Eyebrow_U", FaceRigAnimationSetFlags(True, "_wonder")), # Inner Half eyebrow up, wonder like
    FaceRigAnimationSet("**Eyebrow_U_ext", MIRRORED), # Outer Half eyebrow up
    FaceRigAnimationSet("**EyeClosed", MIRRORED, FaceRigAnimationSetFrames(10)), # Eyelid all the way up at 0, idle at 10, fully closed at 30
    FaceRigAnimationSet("**EyeSquint", MIRRORED), # Eyelid closes slightly at 30, squint
    FaceRigAnimationSet("**EyeWideOpen", MIRRORED), # Eye opens full at 30, eye lids at max
]

eye_and_eyebrows_names = set_to_list(eye_and_eyebrows)

mouth_and_nose_directory = "MouthAndNose"
mouth_and_nose = [
    FaceRigAnimationSet("CheekPuff_*", MIRRORED), # Cheeck Inflates
    FaceRigAnimationSet("Mouth_pursedLips_LR", DEFAULT_FLAGS, IDLE_ROOT), # pursed lips, left 0, 15 centered pursed, 30 right
    FaceRigAnimationSet("Mouth_unveilledTeeth_D", DEFAULT_FLAGS, IDLE_ROOT), # The lower lips moves down
    FaceRigAnimationSet("Mouth_unveilledTeeth_U", DEFAULT_FLAGS, IDLE_ROOT), # The Upper lips move up 
    FaceRigAnimationSet("MouthClosed**_D", FaceRigAnimationSetFlags(True, "_unveilTeeth"), IDLE_ROOT), # Mouth Corner moves down *frown*
    FaceRigAnimationSet("MouthClosed**_D_visime", MIRRORED, IDLE_ROOT), # Mouth closed moves up, while keeping lips together, *less pronounced* used while speech
    FaceRigAnimationSet("MouthClosed**_U", FaceRigAnimationSetFlags(True, "_unveilTeeth"), IDLE_ROOT), # Mouth Corner moves up *smile*
    FaceRigAnimationSet("MouthClosed**_U_visime", MIRRORED, IDLE_ROOT), # Mouth closed moves up, while keeping lips together, *less pronounced* used while speech
    FaceRigAnimationSet("MouthOpen", DEFAULT_FLAGS, IDLE_ROOT), # Mouth Open Idle from 0, to fully open 30
    FaceRigAnimationSet("MouthOpen_base",DEFAULT_FLAGS, IDLE_ROOT), # Mouth stays fully open through from 0 to 30. (Same pose as )
    FaceRigAnimationSet("MouthOpen_pursedLips_LR"),
    FaceRigAnimationSet("MouthOpen**_D", MIRRORED, IDLE_ROOT),
    FaceRigAnimationSet("MouthOpen**_U", MIRRORED, IDLE_ROOT),
    FaceRigAnimationSet("MouthTongueBase", DEFAULT_FLAGS, IDLE_ROOT),
    FaceRigAnimationSet("NoseWrinkler_D", DEFAULT_FLAGS, IDLE_ROOT),
    FaceRigAnimationSet("NoseWrinkler_U", DEFAULT_FLAGS, IDLE_ROOT),
    FaceRigAnimationSet("TongueIdle", DEFAULT_FLAGS, IDLE_ROOT),
    FaceRigAnimationSet("TongueOut_LR", DEFAULT_FLAGS),
    FaceRigAnimationSet("TongueOut_UD", DEFAULT_FLAGS),
]


mouth_and_nose_names = set_to_list(mouth_and_nose)

shoulders_and_hand_directory = "ShouldersAndHand"
shoulders_and_hand = [
    FaceRigAnimationSet("Finger*0_extFlex", MIRRORED), # Ext 0, 15 idle, 30 fist.
    FaceRigAnimationSet("Finger*1_extFlex", MIRRORED), # Ext 0, 15 idle, 30 fist.
    FaceRigAnimationSet("Finger*2_extFlex", MIRRORED), # Ext 0, 15 idle, 30 fist.
    FaceRigAnimationSet("Finger*3_extFlex", MIRRORED), # Ext 0, 15 idle, 30 fist.
    FaceRigAnimationSet("Finger*4_extFlex", MIRRORED), # Ext 0, 15 idle, 30 fist.
    FaceRigAnimationSet("Hand*_closeDown_LR", MIRRORED, IDLE_ROOT), # lowest close
    FaceRigAnimationSet("Hand*_closeMiddle_LR", MIRRORED, IDLE_ROOT), # medium height close
    FaceRigAnimationSet("Hand*_closeUp_LR", MIRRORED),  # max height close
    FaceRigAnimationSet("Hand*_farDown_LR", MIRRORED),
    FaceRigAnimationSet("Hand*_farMiddle_LR", MIRRORED),
    FaceRigAnimationSet("Hand*_farUp_LR", MIRRORED),
    FaceRigAnimationSet("Hand*_solo_LR", MIRRORED),
    FaceRigAnimationSet("Hand*_solo_UD", MIRRORED),
    FaceRigAnimationSet("Hand*_solo_Twist", MIRRORED),
]


shoulders_and_hand_names = set_to_list(shoulders_and_hand)
# start and end frames must match.

## Incorrectly spelled in FaceRig
viseme_directory = "visimes"
visemes = [
    FaceRigAnimationSet("visime_new_AA"),
    FaceRigAnimationSet("visime_new_AH"),
    FaceRigAnimationSet("visime_new_AO"),
    FaceRigAnimationSet("visime_new_AW-OW"),
    FaceRigAnimationSet("visime_new_CH-J-SH"),
    FaceRigAnimationSet("visime_new_EH-AE"),
    FaceRigAnimationSet("visime_new_EY"),
    FaceRigAnimationSet("visime_new_FB"),
    FaceRigAnimationSet("visime_new_FV"),
    FaceRigAnimationSet("visime_new_IH-AY"),
    FaceRigAnimationSet("visime_new_L"),
    FaceRigAnimationSet("visime_new_M-P-B"),
    FaceRigAnimationSet("visime_new_N-NG-DH"),
    FaceRigAnimationSet("visime_new_OY-UH-UW"),
    FaceRigAnimationSet("visime_new_R-ER"),
    FaceRigAnimationSet("visime_new_W"),
    FaceRigAnimationSet("visime_new_X"),
    FaceRigAnimationSet("visime_new_Y-IY"),
]

viseme_names = set_to_list(visemes)
weighted_geometry_append = "_skin"

# Left is Biggest Value (frist frame)
# Right is Smallest value (last frame)
spine_default_constraints = FaceRigBoneConstraints("spine") # Body 
spine_default_constraints.append_constraint(FaceRigBoneValueConstraint(FaceRigConstraintType.ROTATION_X, 20, -10)) # Avatar_FD
spine_default_constraints.append_constraint(FaceRigBoneValueConstraint(FaceRigConstraintType.ROTATION_Z, 16)) # Avatar_LR
spine_default_constraints.append_constraint(FaceRigBoneValueConstraint(FaceRigConstraintType.ROTATION_Y, 35)) # Avatar_Twist

neck_default_constraints = FaceRigBoneConstraints("neck")
neck_default_constraints.append_constraint(FaceRigBoneValueConstraint(FaceRigConstraintType.ROTATION_X, 20, -27)) # Head_UD
neck_default_constraints.append_constraint(FaceRigBoneValueConstraint(FaceRigConstraintType.ROTATION_Z, 17)) # Head_LR
neck_default_constraints.append_constraint(FaceRigBoneValueConstraint(FaceRigConstraintType.ROTATION_Y, 12)) # Head_Twist

head_default_constraints = FaceRigBoneConstraints("head")
head_default_constraints.append_constraint(FaceRigBoneValueConstraint(FaceRigConstraintType.ROTATION_X, 18.5, -35)) # Head_UD
head_default_constraints.append_constraint(FaceRigBoneValueConstraint(FaceRigConstraintType.ROTATION_Z, 17)) # Head_LR
head_default_constraints.append_constraint(FaceRigBoneValueConstraint(FaceRigConstraintType.ROTATION_Y, 37.5)) # Head_Twist

left_eye_default_constraints = FaceRigBoneConstraints("left_eye")
right_eye_default_constraints = FaceRigBoneConstraints("right_eye")

left_eye_default_constraints.append_constraint(FaceRigBoneValueConstraint(FaceRigConstraintType.ROTATION_X, 40, -27)) # LeftEye_UD
right_eye_default_constraints.append_constraint(FaceRigBoneValueConstraint(FaceRigConstraintType.ROTATION_X, 40, -27)) # RightEye_UD

# Left is Biggest Value (frist frame)
# Right is Smallest value (last frame)
left_eye_default_constraints.append_constraint(FaceRigBoneValueConstraint(FaceRigConstraintType.ROTATION_Y, 26, -55)) # LeftEye_LR
right_eye_default_constraints.append_constraint(FaceRigBoneValueConstraint(FaceRigConstraintType.ROTATION_Y, 55, -26)) # RightEye_LR


avatar_default_constraint_set = [spine_default_constraints]
head_default_constraint_set = [neck_default_constraints, head_default_constraints]
eyes_default_constraint_set = [left_eye_default_constraints, right_eye_default_constraints]