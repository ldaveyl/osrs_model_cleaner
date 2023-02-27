import bpy

from bpy.props import StringProperty
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper


class OSRSMC_OT_Load_Model(Operator, ImportHelper):
    bl_idname = "object.load_model"
    bl_label = "Load Model"
    filter_glob: StringProperty(
        default='*.obj',
        options={'HIDDEN'}
    )

    def execute(self, context):
        bpy.ops.import_scene.obj(filepath=self.filepath)
        return {"FINISHED"}


class OSRSMC_OT_Merge_Materials(Operator):
    bl_idname = "object.merge_materials"
    bl_label = "Merge Materials"

    def execute(self, context):
        if not context.scene.osrs_model:
            self.report({"ERROR"}, "Please select an OSRS Model")
            return {"CANCELLED"}
        mesh = context.scene.osrs_model.data

        # Extract materials and colors from mesh
        mat_dict = {}
        for f in mesh.polygons:
            slot = context.scene.osrs_model.material_slots[f.material_index]
            mat = slot.material
            mat_dict[f.material_index] = list(mat.diffuse_color)

        print(mat_dict)

        # Group materials based on rgb values of principled bsdf

        return {"FINISHED"}
