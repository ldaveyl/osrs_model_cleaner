import numpy as np

def find_optimal_k(cluster_dict):
    max_silhouette = -np.inf
    for k in cluster_dict.keys():
        if cluster_dict[k]["silhouette"] > max_silhouette:
            max_silhouette = cluster_dict[k]["silhouette"]
            optimal_k = k
    return optimal_k