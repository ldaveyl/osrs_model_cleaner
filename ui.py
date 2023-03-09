import bpy

from bpy.types import Panel


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
        col.prop_search(context.scene, "osrs_model",
            context.scene, "objects", icon="OBJECT_DATA")


class OSRSMC_PT_Panel_Merge_Materials(OSRSMC_PT_Panel, Panel):
    bl_parent_id = "OSRSMC_PT_Panel_Load_Model"
    bl_label = "Merge Materials"

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.prop(context.scene, "find_optimal_k")

        row = layout.row()
        col = row.column()
        col.prop(context.scene, "k")
        if context.scene.find_optimal_k:
            col.enabled = False

        row = layout.row()
        col = row.column()
        col.prop(context.scene, "freq_weight")

        row3 = layout.row()
        col = row3.column()
        col.operator("object.merge_materials",
            text="Merge Materials", icon="RNDCURVE")

