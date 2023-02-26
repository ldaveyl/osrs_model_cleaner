# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "osrs_model_cleaner",
    "author" : "Lucas Davey",
    "description" : "",
    "blender" : (3, 4, 0),
    "version" : (0, 0, 1),
    "location" : "View3D",
    "warning" : "",
    "category" : "Generic"
}

import bpy

from bpy.props import StringProperty, PointerProperty
from bpy.types import Panel, Operator
from bpy_extras.io_utils import ImportHelper

C = bpy.context

class OSRSMC_PT_Panel:
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "OSRSMC"
    bl_category = "OSRSMC"
    
class OSRSMC_PT_Panel_Load_Model(OSRSMC_PT_Panel, Panel):
    bl_idname = "OSRSMC_PT_Panel_Load_Model"
    bl_label = "OSRSMC"
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        col = row.column()
        col.operator("object.load_model", text="Load Model", icon="FILE")
        
class OSRSMC_PT_Panel_Merge_Materials(OSRSMC_PT_Panel, Panel):
    bl_parent_id = "OSRSMC_PT_Panel_Load_Model"
    bl_label = "Merge Materials"
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        col = row.column()
        col.prop_search(C.scene, "osrs_model", C.scene, "objects", icon="OBJECT_DATA")
        col.operator("object.merge_materials", text="Merge Materials", icon="RNDCURVE")
        
class OSRSMC_OT_Load_Model(Operator, ImportHelper):
    bl_idname = "object.load_model"
    bl_label = "Load Model"
    filter_glob: StringProperty( 
        default='*.obj', 
        options={'HIDDEN'} 
    )
    def execute(self, context):
        bpy.ops.import_scene.obj(filepath = self.filepath)
        return { "FINISHED" }

classes = (
    OSRSMC_PT_Panel_Load_Model,
    OSRSMC_PT_Panel_Merge_Materials,
    OSRSMC_OT_Load_Model
)

props = [
    ("osrs_model", PointerProperty(name="OSRS Model", type=bpy.types.Object))
]

def register():
    for c in classes:
        bpy.utils.register_class(c)
        
    for (prop_name, prop_value) in props:
        setattr(bpy.types.Scene, prop_name, prop_value)
        
def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
      
if __name__ == "__main__":
    register()