import bpy
import numpy as np

from bpy.props import StringProperty
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper
from colorsys import rgb_to_hsv, hsv_to_rgb

from . import constants


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

        # Extract materials from mesh
        # TODO: link polygons with materials ...
        mesh = context.scene.osrs_model.data
        original_materials_list = []
        hsv_lst = []
        for f in mesh.polygons:
            slot = context.scene.osrs_model.material_slots[f.material_index]
            original_materials_list.append(slot.material)
            # Subset to remove alpha
            rgb = list(slot.material.diffuse_color)[:-1]
            hsv = rgb_to_hsv(rgb[0], rgb[1], rgb[2])
            hsv_lst.append(hsv)
        hsv_mat = np.array(hsv_lst)

        # Make sure that sklearn is correctly installed
        try:
            from sklearn.cluster import KMeans
            from sklearn.metrics import silhouette_score
        except ModuleNotFoundError as error:
            self.report({"ERROR"}, f"Failed to import sklearn: {error}")
            return {"CANCELLED"}

        # Cluster hsv values for different number of clusters
        cluster_dict = {}
        for k in range(constants.min_clusters,
                       context.scene.max_n_clusters + 1):

            # Calculate clusters
            kmeans = KMeans(n_clusters=k, random_state=0,
                            n_init="auto").fit(hsv_mat)

            # Calculate silhouette score
            silhouette = silhouette_score(
                hsv_mat, kmeans.labels_, metric="euclidean")

            # Calculate distance matrix to all centroids
            dist_to_centroids_mat = kmeans.transform(hsv_mat)

            # Calculate for each centroid the hsv
            # within that cluster that is closest to it
            closest_hsv_lst = []
            for centroid in range(k):
                smallest_dist = np.inf
                for i, dist_to_centroids in enumerate(dist_to_centroids_mat):
                    if kmeans.labels_[i] == centroid and \
                       dist_to_centroids[centroid] < smallest_dist:
                        smallest_dist = dist_to_centroids[centroid]
                        closest_hsv = hsv_mat[i, :]
                closest_hsv_lst.append(closest_hsv)

            # Log results
            cluster_dict[k] = {}
            cluster_dict[k]["closest_hsv_lst"] = closest_hsv_lst
            cluster_dict[k]["cluster_labels"] = kmeans.labels_
            cluster_dict[k]["silhouette"] = silhouette

        # Find optimal k
        max_k = -np.inf
        for k in cluster_dict.keys():
            if cluster_dict[k]["silhouette"] > max_k:
                max_k = cluster_dict[k]["silhouette"]
                optimal_k = k

        # Remove all materials
        context.scene.osrs_model.data.materials.clear()

        # Set new materials
        for i, hsv in enumerate(cluster_dict[optimal_k]["closest_hsv_lst"]):
            # Convert back to rgb and add alpha
            rgb = hsv_to_rgb(hsv[0], hsv[1], hsv[2])
            rgb = np.append(rgb, 1.0)
            mat = bpy.data.materials.new(name=f"mat{i}")
            mat.use_nodes = True
            principled_bsdf = mat.node_tree.nodes.get("Principled BSDF")
            principled_bsdf.inputs[0].default_value = rgb

        # for f in mesh.polygons:

        # print(context.scene.osrs_model.data.materials)

        # for i in range(len(context.scene.osrs_model.material_slots)):
        #     context.scene.osrs_model.activate_material_index = i
        #     break

        # for slot in context.scene.osrs_model.material_slots:
            # print(slot)

        return {"FINISHED"}
