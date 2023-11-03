from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import numpy as np
import os

os.environ["TOKENIZERS_PARALLELISM"] = "false"

def cluster_skills(skills):
    # Load the pre-trained sentence embedding model
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Generate embeddings for each skill
    embeddings = model.encode(skills)
    
    # Determine the optimal number of clusters using silhouette scores
    silhouette_scores = []
    K = range(2, len(skills))  # Clustering at least into 2 clusters and at most 10 or the number of skills we have
    
    for k in K:
        # Explicitly set n_init to 10 to suppress future warning and retain current behavior
        km = KMeans(n_clusters=k, n_init='auto')
        cluster_labels = km.fit_predict(embeddings)
        silhouette_avg = silhouette_score(embeddings, cluster_labels)
        silhouette_scores.append(silhouette_avg)
        
    # Find the optimal number of clusters based on the highest silhouette score
    optimal_k = K[np.argmax(silhouette_scores)]
    
    # Perform K-means clustering with the optimal number of clusters
    kmeans = KMeans(n_clusters=optimal_k)
    kmeans.fit(embeddings)
    cluster_labels = kmeans.labels_
    
    # Create a dictionary to store cluster information
    clusters = {}
    for skill, label in zip(skills, cluster_labels):
        if label not in clusters:
            clusters[label] = []
        clusters[label].append(skill)
    
    # Convert clusters dictionary to a list for easy display
    cluster_list = [(label, cluster) for label, cluster in clusters.items()]

    return cluster_list

if __name__ == '__main__':
    skills = ["Python", "Python Developer", "Software engineering", "Java", "Javascript", "JS", "Professional Communication"]
    clustered_skills = cluster_skills(skills)
    print("Clustered Skills:", clustered_skills)
