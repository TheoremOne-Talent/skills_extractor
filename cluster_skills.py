from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from collections import Counter
import numpy as np
import os
from scipy.spatial import distance

os.environ["TOKENIZERS_PARALLELISM"] = "false"

def cluster_skills(skills):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(skills)
    
    silhouette_scores = []
    K = range(2, len(skills))
    
    for k in K:
        km = KMeans(n_clusters=k, init='k-means++', n_init=10)
        cluster_labels = km.fit_predict(embeddings)
        silhouette_avg = silhouette_score(embeddings, cluster_labels)
        silhouette_scores.append(silhouette_avg)
        
    optimal_k = K[np.argmax(silhouette_scores)]
    kmeans = KMeans(n_clusters=optimal_k, init='k-means++', n_init=10)
    kmeans.fit(embeddings)
    cluster_labels = kmeans.labels_
    
    clusters = {}
    for skill, label in zip(skills, cluster_labels):
        clusters.setdefault(label, []).append(skill)
    
    # Assigning semantically accurate names to clusters using the skill closest to the centroid
    cluster_names = {}
    for label in clusters:
        centroid = kmeans.cluster_centers_[label]
        # Calculate distances of all skills in the cluster to the centroid
        distances = [distance.euclidean(centroid, model.encode(skill)) for skill in clusters[label]]
        # Get the skill with the minimum distance to the centroid
        closest_skill = clusters[label][np.argmin(distances)]
        cluster_names[label] = closest_skill

    # Convert clusters to a list with assigned names
    cluster_list_with_names = [(cluster_names[label], cluster) for label, cluster in clusters.items()]

    return cluster_list_with_names

if __name__ == '__main__':
    skills = ["Python", "Python Developer", "Software engineering", "Java", "Javascript", "JS", "Professional Communication"]
    clustered_skills = cluster_skills(skills)
    print("Clustered Skills with Names:", clustered_skills)
