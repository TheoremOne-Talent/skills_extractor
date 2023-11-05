from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from collections import Counter
import numpy as np
import os
from scipy.spatial import distance
from tqdm import tqdm
from joblib import Parallel, delayed
from sklearn.decomposition import PCA
import warnings
warnings.filterwarnings("ignore")


os.environ["TOKENIZERS_PARALLELISM"] = "false"

def calculate_silhouette(k, pca_embeddings):
    km = KMeans(n_clusters=k, init='k-means++', n_init=10)
    cluster_labels = km.fit_predict(pca_embeddings)
    silhouette_avg = silhouette_score(pca_embeddings, cluster_labels)
    return silhouette_avg

def cluster_skills(skills, n_clusters=2):
    print("[INFO] Encoding skills...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(skills)
    
    print("[INFO] Computing PCA for all components...")
    pca = PCA()
    pca.fit(embeddings)
    
    # Determine the number of components to retain 95% of the variance
    cumsum = np.cumsum(pca.explained_variance_ratio_)
    d = np.argmax(cumsum >= 0.95) + 1
    print(f"[INFO] Optimal number of PCA components to retain 95% variance: {d}")
    
    # Apply PCA with the optimal number of components
    pca = PCA(n_components=d)
    pca_embeddings = pca.fit_transform(embeddings)

    # Adjusting K to potentially allow more clusters
    if n_clusters is None or n_clusters < 3:
        K = range(2, len(skills))
    else:
        K = range(2, n_clusters)
    print(f"[INFO] Calculating silhouette scores for k values: {list(K)}")
    
    # Parallelize silhouette score calculation
    silhouette_scores = Parallel(n_jobs=-1)(delayed(calculate_silhouette)(k, pca_embeddings) for k in K)
    
    optimal_k = K[np.argmax(silhouette_scores)]
    print(f"[INFO] Optimal number of clusters: {optimal_k}")
    
    kmeans = KMeans(n_clusters=optimal_k, init='k-means++', n_init=10)
    kmeans.fit(pca_embeddings)
    cluster_labels = kmeans.labels_
    
    clusters = {}
    for skill, label in zip(skills, cluster_labels):
        clusters.setdefault(label, []).append(skill)

    cluster_names = {}
    for label in clusters:
        centroid = kmeans.cluster_centers_[label]
        transformed_skill_embeddings = pca.transform(model.encode(clusters[label]))
        distances = [distance.euclidean(centroid, transformed_skill) for transformed_skill in transformed_skill_embeddings]
        
        closest_skill = clusters[label][np.argmin(distances)]
        cluster_names[label] = closest_skill

    cluster_list_with_names = [(cluster_names[label], cluster) for label, cluster in clusters.items()]
    print("[INFO] Clustering complete.")
    return cluster_list_with_names

if __name__ == '__main__':
    skills = ["Python", "Python Developer", "Software engineering", "Java", "Javascript", "JS", "Professional Communication"]
    clustered_skills = cluster_skills(skills)
    print("Clustered Skills with Names:", clustered_skills)
