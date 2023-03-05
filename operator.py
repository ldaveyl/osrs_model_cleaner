import bpy
import numpy as np

from bpy.props import StringProperty
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper
from colorsys import rgb_to_hsv

from . import functions

class OSRSMC_OT_Load_Model(Operator, ImportHelper):
    bl_idname = "object.load_model"
    bl_label = "Load Model"
    filter_glob: StringProperty(
        default='*.obj',
        options={'HIDDEN'}
    )

    def execute(self, context):
        # Import .obj and select as OSRS model
        # TODO - verify that obj is from Runelite, 
        bpy.ops.import_scene.obj(filepath=self.filepath)
        bpy.context.scene.osrs_model = bpy.context.selected_objects[0]
        return {"FINISHED"}


class OSRSMC_OT_Merge_Materials(Operator):
    bl_idname = "object.merge_materials"
    bl_label = "Merge Materials"

    def execute(self, context):
        if not context.scene.osrs_model:
            self.report({"ERROR"}, "Please select an OSRS Model")
            return {"CANCELLED"}
        mesh = context.scene.osrs_model.data

        # Extract colors from mesh
        rgb_lst = []
        hsv_lst = []
        for f in mesh.polygons:
            slot = context.scene.osrs_model.material_slots[f.material_index]
            # Subset to remove alpha
            rgb = list(slot.material.diffuse_color)[:-1]
            hsv = rgb_to_hsv(rgb[0], rgb[1], rgb[2])
            rgb_lst.append(rgb)
            hsv_lst.append(hsv)

        rgb_mat = np.array(rgb_lst)
        hsv_mat = np.array(hsv_lst)

        # Cluster rgb values
        # centroids_dict = {}
        # for n_clusters in range(1, context.scene.max_n_clusters + 1):
        #     kmeans = functions.KMeans(n_clusters=n_clusters)
        #     kmeans.fit(hsv_mat)
        #     centroids_dict[n_clusters] = 
            





        # hsv_mat = rgb_to_hsv
        # np.savetxt("C:\\Users\\lucas\\Documents\\MyBlenderStuff\\osrs_model_cleaner\\foo.csv", rgb_mat, delimiter=",")

        # Group materials based on rgb values of principled bsdf

        return {"FINISHED"}
