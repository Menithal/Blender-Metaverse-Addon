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

## Build the File Loading Operator, and allows for File Selection
# By Matti 'Menithal' Lahtinen

import bpy

import json
import os

from bpy.props import (
        StringProperty,
        BoolProperty,
        FloatProperty,
        EnumProperty,
)
        
from bpy_extras.io_utils import (
    ImportHelper
)


from hifi_scene import *

class HifiJsonOperator(bpy.types.Operator, ImportHelper):
    
    # Load a Hifi File
    bl_idname = "import_scene.hifi"
    bl_label = "Import Hifi Json"
    bl_options = {"UNDO", "PRESET"}
    
    directory = StringProperty()
    
    filename_ext = ".json"
    filter_glob = StringProperty(default="*.json", options={'HIDDEN'})
    
    uv_sphere = BoolProperty( 
        name = "Use UV Sphere",
        description = "Uses UV Sphere instead of Quad Sphere",
        default = False,
    )
    
    join_children = BoolProperty( 
        name = "Join Mesh Children",
        description = "Joins Child Mesh with their parents to form a single object. Instead of keeping everything separate",
        default = True,
    )
    
    merge_distance = FloatProperty(
        name = "Merge Distance",
        description = "Merge close vertices together",
        min = 0.0, max = 1.0,
        default = 0.001,
    )
    
    delete_interior_faces = BoolProperty(
        name = "Delete interior Faces",
        description = "If Mesh is made whole with Merge, make sure to remove interior faces",
        default = True,
    )
    
    use_boolean_operation = EnumProperty(
        items=(('NONE', "None", "Do not use boolean operations"),
               ('CARVE', "Carve", "EXPERIMENTAL: Use CARVE boolean Operation to join mesh"),
               ('BMESH', "BMesh", "EXPERIMENTAL: Use BMESH boolean Operation to join mesh")),
        name = "Boolean",
        description = "EXPERIMENTAL: Enable Boolean Operation when joining parents",
        )    
    
    def draw (self, context):
        layout = self.layout
        
        sub = layout.column()
        
        sub.prop(self, "uv_sphere")
        sub.prop(self, "join_children")
        
        sub.prop(self, "merge_distance")
        
        sub.prop(self, "delete_interior_faces")
        sub.prop(self, "use_boolean_operation")

    def execute(self, context):
        keywords = self.as_keywords(ignore=("filter_glob", "directory"))
        return load_file(self, context, **keywords)


def load_file(operator, context, filepath="",
              uv_sphere= False,
              join_children=True, 
              merge_distance = 0.01, 
              delete_interior_faces = True,
              use_boolean_operation = 'NONE'):
                  
    json_data = open(filepath).read()
    data = json.loads(json_data)
    
    scene = HifiScene(data, uv_sphere, join_children, merge_distance, delete_interior_faces, use_boolean_operation)
    return {"FINISHED"}

