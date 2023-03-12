import bpy
import numpy as np

from bpy.props import StringProperty
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper
from colorsys import rgb_to_hsv, hsv_to_rgb

from . import constants
from . import functions

import sklearn
# from sklearn.cluster import KMeans
# from sklearn.metrics import silhouette_score

class OSRSMC_OT_Load_Model(Operator, ImportHelper):
    bl_idname = "object.load_model"
    bl_label = "Load Model"
    filter_glob: StringProperty(default='*.obj', options={'HIDDEN'})

    def execute(self, context):
        # Import .obj and select as OSRS model
        bpy.ops.import_scene.obj(filepath=self.filepath)
        bpy.context.scene.target = bpy.context.selected_objects[0]
        return {"FINISHED"}


class OSRSMC_OT_Merge_Materials(Operator):
    bl_idname = "object.merge_materials"
    bl_label = "Merge Materials"

    def execute(self, context):

        # Check that a target was selected
        if not context.scene.target:
            self.report({"ERROR"}, "Please select a target")
            return {"CANCELLED"}
        
        # Check that model exists
        if not context.scene.target.name in \
          bpy.context.scene.objects.keys():
            context.scene.target = None
            self.report({"ERROR"}, "Object not found in scene")
            return {"CANCELLED"}
        
        # Create list of colors for each face
        hsv_lst = []
        for p in context.scene.target.data.polygons:
            slot = context.scene.target.material_slots[p.material_index]
            # Subset to remove alpha
            rgb = list(slot.material.diffuse_color)[:-1]
            hsv = rgb_to_hsv(rgb[0], rgb[1], rgb[2])
            hsv_lst.append(hsv)
        hsv_lst = np.array(hsv_lst)

        # Extract colors from model
        # hsv_lst = []
        # for mat in context.scene.target.data.materials:
        #     rgb = list(mat.diffuse_color)[:-1]
        #     hsv = rgb_to_hsv(rgb[0], rgb[1], rgb[2])
        #     hsv_lst.append(hsv)
        # hsv_lst = np.array(hsv_lst)
        # print(len(hsv_lst))

        # Map polygons to materials
        polygon_to_material = {}
        for p in context.scene.target.data.polygons:
            polygon_to_material[p.index] = p.material_index

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
            cluster_dict[k]["cluster_centroids"] = kmeans.cluster_centers_
            cluster_dict[k]["silhouette"] = silhouette

        # Find optimal k
        if context.scene.find_optimal_k:
            context.scene.k = functions.find_optimal_k(cluster_dict)

        # Remove all materials
        context.scene.target.data.materials.clear()

        # Create new materials
        for i, hsv in enumerate(cluster_dict[context.scene.k]["closest_hsv_lst"]):
            
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
            context.scene.target.data.materials.append(mat)

        # Assign new materials
        for p in context.scene.target.data.polygons:
            original_mat_idx = polygon_to_material[p.index]
            print(p.index, polygon_to_material[p.index])
            new_mat_idx = cluster_dict[context.scene.k]["cluster_labels"][original_mat_idx]
            p.material_index = new_mat_idx


        print(len(cluster_dict[context.scene.k]["cluster_labels"]))
        
        ######################################
        ## DEV
        ######################################
        
        import plotly
        import plotly.express as px
        import pandas as pd

        data_df = pd.DataFrame(data=hsv_lst, columns=["h", "s", "v"])
        data_df["type"] = "data"
        data_df["label"] = cluster_dict[context.scene.k]["cluster_labels"]

        centroids_df = pd.DataFrame(cluster_dict[context.scene.k]["cluster_centroids"], columns=["h", "s", "v"])
        centroids_df["type"] = "centroid"
        centroids_df["label"] = range(context.scene.k)

        df = pd.concat([data_df, centroids_df]).reset_index(drop=True)
        df["col_hsv"] = list(zip(df["h"], df["s"], df["v"]))
        df["col_rgb"] = df["col_hsv"].apply(lambda x: hsv_to_rgb(x[0], x[1], x[2]))

        fig = px.scatter_3d(df, x="h", y="s", z="v", symbol="type")
        fig.update_traces(marker=dict(color=df["label"]))
        # plotly.offline.plot(fig, filename='C:\\Users\\lucas\\Documents\\MyBlenderStuff\\myplot.html')

        print("optimal_k:", context.scene.k )

        # TODO: optimize clustering -> too many clusters are missed ...
        # Perhaps add way to give more weight to all clusters -> frequency based? 

        return {"FINISHED"}