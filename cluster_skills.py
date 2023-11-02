from sentence_transformers import SentenceTransformer
import hdbscan

def cluster_skills(skills):
    # Load a pre-trained sentence embedding model
    model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
    
    # Generate embeddings for each skill
    embeddings = model.encode(skills)
    
    # Use HDBSCAN to cluster these embeddings
    clusterer = hdbscan.HDBSCAN(min_cluster_size=2, metric='euclidean', cluster_selection_method='eom').fit(embeddings)
    
    # Dictionary to store merged skills
    merged_skills = {}

    # Iterate through each skill and its corresponding cluster label
    for skill, label in zip(skills, clusterer.labels_):
        # If the label is -1, the point is considered an outlier and won't be merged with other skills
        if label == -1:
            merged_skills[skill] = skill
        else:
            # Use the most frequent skill in the cluster as the representative skill
            representative_skill = max([s for s, l in zip(skills, clusterer.labels_) if l == label], key=skills.count)
            merged_skills[skill] = representative_skill
            
    return set(merged_skills.values())

skills = ["Python", "Pyton", "Java", "Javascript", "JS"]
print(cluster_skills(skills))
