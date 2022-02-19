
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

# Copyright 2021 Matti 'Menithal' Lahtinen

import bpy

def set_optional_area_context_type(target_mode):
    area_type = bpy.context.area.type

    # If this is triggered above, then
    if area_type == "":
        return

    bpy.context.area.type = target_mode


def toggle_console():
    try:
        bpy.ops.wm.console_toggle()
    except:
        print("Console was toggled but not available on windows.")
        