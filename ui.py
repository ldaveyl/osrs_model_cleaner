import bpy

from bpy.types import Panel, UIList


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
        col.prop_search(bpy.context.scene, "osrs_model",
                bpy.context.scene, "objects", icon="OBJECT_DATA")


class OSRSMC_PT_Panel_Merge_Materials(OSRSMC_PT_Panel, Panel):
    bl_parent_id = "OSRSMC_PT_Panel_Load_Model"
    bl_label = "Merge Materials"

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        col = row.column()
        col.operator("object.merge_materials",
                     text="Merge Materials", icon="RNDCURVE")
        row.prop(context.scene, "max_n_clusters")
        

class OSRSMC_UL_Materials_List(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {"DEFAULT", "COMPACT"}:
            row = layout.row()
            row.prop(item.material_ptr, "name", text="", emboss=False, icon_value=layout.icon(item.material_ptr))
        elif self.layout_type in {"GRID"}:
            layout.alignment = "CENTER"
            layout.prop(item.material_ptr, "name", text="", emboss=False, icon_value=layout.icon(item.material_ptr))
        
        
