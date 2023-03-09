import bpy
import numpy as np

from bpy.props import StringProperty
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper
from colorsys import rgb_to_hsv, hsv_to_rgb

from . import constants
from . import functions

class OSRSMC_OT_Load_Model(Operator, ImportHelper):
    bl_idname = "object.load_model"
    bl_label = "Load Model"
    filter_glob: StringProperty(default='*.obj', options={'HIDDEN'})

    def execute(self, context):
        # Import .obj and select as OSRS model
        bpy.ops.import_scene.obj(filepath=self.filepath)
        bpy.context.scene.osrs_model = bpy.context.selected_objects[0]
        return {"FINISHED"}


class OSRSMC_OT_Merge_Materials(Operator):
    bl_idname = "object.merge_materials"
    bl_label = "Merge Materials"

    def execute(self, context):

        # Check that a model was selected
        if not context.scene.osrs_model:
            self.report({"ERROR"}, "Please select an OSRS Model")
            return {"CANCELLED"}
        
        # Check that model exists
        if not context.scene.osrs_model.name in \
          bpy.context.scene.objects.keys():
            context.scene.osrs_model = None
            self.report({"ERROR"}, "Object not found in scene")
            return {"CANCELLED"}
        
        # Create list of colors for each face
        hsv_lst = []
        for p in context.scene.osrs_model.data.polygons:
            slot = context.scene.osrs_model.material_slots[p.material_index]
            # Subset to remove alpha
            rgb = list(slot.material.diffuse_color)[:-1]
            hsv = rgb_to_hsv(rgb[0], rgb[1], rgb[2])
            hsv_lst.append(hsv)
        hsv_lst = np.array(hsv_lst)

        # Remove duplicates if not weighting by frequency
        if not context.scene.freq_weight:
            hsv_lst = np.unique(hsv_lst, axis=0)

        # Extract colors from model
        hsv_lst = []
        for mat in context.scene.osrs_model.data.materials:
            rgb = list(mat.diffuse_color)[:-1]
            hsv = rgb_to_hsv(rgb[0], rgb[1], rgb[2])
            hsv_lst.append(hsv)
        hsv_lst = np.array(hsv_lst)

        # Map polygons to materials
        polygon_to_material = {}
        for p in context.scene.osrs_model.data.polygons:
            polygon_to_material[p.index] = p.material_index

        # Make sure that sklearn is correctly installed
        try:
            from sklearn.cluster import KMeans
            from sklearn.metrics import silhouette_score
        except ModuleNotFoundError as error:
            self.report({"ERROR"}, f"Failed to import sklearn: {error}")
            return {"CANCELLED"}

        # Cluster hsv values for different number of clusters
        cluster_dict = {}
        for k in range(constants.min_k, constants.max_k + 1):

            # Calculate clusters
            kmeans = KMeans(n_clusters=k, random_state=0,
                n_init="auto").fit(hsv_lst)

            # Calculate silhouette score
            silhouette = silhouette_score(
                hsv_lst, kmeans.labels_, metric="euclidean")

            # Calculate distance matrix to all centroids
            dist_to_centroids_matrix = kmeans.transform(hsv_lst)

            # Calculate for each centroid the hsv
            # within that cluster that is closest to it
            closest_hsv_lst = []
            for centroid in range(k):
                smallest_dist = np.inf
                for i, dist_to_centroids in enumerate(dist_to_centroids_matrix):
                    if kmeans.labels_[i] == centroid and \
                       dist_to_centroids[centroid] < smallest_dist:
                        smallest_dist = dist_to_centroids[centroid]
                        closest_hsv = hsv_lst[i, :]
                closest_hsv_lst.append(closest_hsv)

            # Log results
            cluster_dict[k] = {}
            cluster_dict[k]["closest_hsv_lst"] = closest_hsv_lst
            cluster_dict[k]["cluster_labels"] = kmeans.labels_
            cluster_dict[k]["silhouette"] = silhouette

        # Find optimal k
        if context.scene.find_optimal_k:
            context.scene.k = functions.find_optimal_k(cluster_dict)

        # Remove all materials
        context.scene.osrs_model.data.materials.clear()

        # Create new materials
        for i, hsv in enumerate(cluster_dict[context.scene.k ]["closest_hsv_lst"]):
            
            # Convert hsv to rgb and add alpha
            rgb = hsv_to_rgb(hsv[0], hsv[1], hsv[2])
            rgb = np.append(rgb, 1.0)

            # Create principled bsdf
            mat = bpy.data.materials.new(name=f"mat{i}")
            mat.use_nodes = True
            principled_bsdf = mat.node_tree.nodes.get("Principled BSDF")
            principled_bsdf.inputs[0].default_value = rgb # Base Color
            principled_bsdf.inputs[7].default_value = 0 # Specular
            principled_bsdf.inputs[9].default_value = 1 # Roughness

            # Set colour in solid view
            mat.diffuse_color = rgb

            # Add material
            context.scene.osrs_model.data.materials.append(mat)

        # Assign new materials
        for p in context.scene.osrs_model.data.polygons:
            original_mat_idx = polygon_to_material[p.index]
            new_mat_idx = cluster_dict[context.scene.k ]["cluster_labels"][original_mat_idx]
            p.material_index = new_mat_idx

        print("optimal_k:", context.scene.k )

        # TODO: optimize clustering -> too many clusters are missed ...
        # Perhaps add way to give more weight to all clusters -> frequency based? 
        # Low priority: Figure out how to assign colours in object mode (i.e. the preview)
    
        # print(context.scene.osrs_model.data.materials)

        # for i in range(len(context.scene.osrs_model.material_slots)):
        #     context.scene.osrs_model.activate_material_index = i
        #     break

        # for slot in context.scene.osrs_model.material_slots:
            # print(slot)

        return {"FINISHED"}
