import pandas as pd
import logging
from cluster_skills import cluster_skills

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def read_skills_taxonomy(file_path):
    """
    Read skills from a text file.
    :param file_path: Path to the file containing skills taxonomy.
    :return: A list of unique skills.
    """
    try:
        with open(file_path, "r") as r:
            lines = r.readlines()
            skills_list = [line.strip("\n") for line in lines]
            return list(set(skills_list))
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        raise
    except Exception as e:
        logging.error(f"Error reading {file_path}: {e}")
        raise

def cluster_and_label_skills(skills_list, n_clusters=200):
    """
    Cluster and label the skills using the provided clustering function.
    :param skills_list: A list of skills to be clustered.
    :param n_clusters: Number of clusters to divide the skills into.
    :return: A dictionary mapping each skill to its cluster label.
    """
    try:
        clusters = cluster_skills(skills_list, n_clusters=n_clusters)
        return {skill: cluster_name for cluster_name, skills in clusters for skill in skills}
    except Exception as e:
        logging.error(f"Error clustering skills: {e}")
        raise

def process_individual_skills(df, skill_to_cluster_label):
    """
    Process a dataframe of individual skills to map them to the cluster labels.
    :param df: Dataframe with individual skills.
    :param skill_to_cluster_label: Dictionary mapping skills to cluster labels.
    :return: A dictionary with names as keys and a list of their clustered skills as values.
    """
    individual_skills = {}
    for idx, row in df.iterrows():
        try:
            skills = row['Skills'].split(", ") if isinstance(row["Skills"], str) else []
            clustered_skills = [skill_to_cluster_label.get(skill, skill) for skill in skills]
            individual_skills[row["Name"]] = list(set(clustered_skills))
        except Exception as e:
            logging.error(f"Error processing row {idx}: {e}")
            # Optionally continue to next row or raise an exception
    return individual_skills

def main():
    """
    Main function to read skills, cluster them, and process individual skills.
    """
    try:
        skills_taxonomy_file = "skills_taxonomy.txt"
        individual_skills_file = "individual_skills.csv"

        # Read skills taxonomy
        skills_list_unique = read_skills_taxonomy(skills_taxonomy_file)

        logging.info(f"Unique skills count: {len(skills_list_unique)}")

        # Cluster skills
        skill_to_cluster_label = cluster_and_label_skills(skills_list_unique)
        skills_taxonomy = set(skill_to_cluster_label.values())

        # Read individual skills data
        df = pd.read_csv(individual_skills_file)

        # Process individual skills
        individual_skills = process_individual_skills(df, skill_to_cluster_label)

        # Write refined skills taxonomy
        with open("skills_taxonomy_refined.txt", "w") as f:
            for skill in skills_taxonomy:
                f.write(skill + "\n")

        # Create dataframe for individual skills and save to CSV
        individual_skills_df = pd.DataFrame({
            'Name': individual_skills.keys(),
            'Skills': [', '.join(skills) for skills in individual_skills.values()]
        })

        individual_skills_df.to_csv("individual_skills_refined.csv", index=False)
        
    except Exception as e:
        logging.error(f"An error occurred in main: {e}")

if __name__ == '__main__':
    main()
