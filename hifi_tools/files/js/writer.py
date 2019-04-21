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

## TODO- Convert to use native flow.
js_flow = "flow.js"
js_flow_library = "VectorMath.js"
js_custom_writer = "//__PYTHONFILL__CUSTOM_SETS__//"


class FlowData:
    active = True
    stiffness = 0.0
    radius = 0.04
    gravity = -0.035
    damping = 0.8
    inertia = 0.8
    delta = 0.35

class Vec3Data:
    x = 0
    y = 0
    z = 0

class CollisionData:
    _type = "sphere"
    radius = 0.14
    offset = Vec3Data()

def js_writer(flow_data, collision_data):
    print("Open JS Writer")

