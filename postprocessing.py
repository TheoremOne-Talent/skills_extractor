import argparse
import pandas as pd
import logging
from cluster_skills import cluster_skills
import os
from datetime import datetime

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
        clusters = cluster_skills(skills_list, n_clusters=n_clusters, use_pca=True)
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

def format_and_sort_skills(skills):
    """
    Format skills with proper capitalization and sort them alphabetically.
    :param skills: A list or set of skills.
    :return: A sorted list of skills with proper capitalization.
    """
    # Assuming the capitalization rule is to capitalize the first letter of each skill
    formatted_skills = [skill.capitalize() for skill in skills]
    # Sort the skills alphabetically
    return sorted(formatted_skills)

def write_skills_to_file(skills, file_path):
    """
    Write skills to a file, sorted and formatted.
    :param skills: A list or set of skills.
    :param file_path: File path to write the skills to.
    """
    with open(file_path, "w") as f:
        for skill in skills:
            f.write(skill + "\n")

def get_timestamped_filename(directory, original_filename):
    """
    Generate a timestamped filename if the original file exists, to avoid overwriting.
    :param original_filename: The original file name.
    :return: A tuple containing the new filename to use and the renamed old file.
    """
    base_filename, file_extension = os.path.splitext(original_filename)
    timestamped_filename = f"{base_filename}_{datetime.now().strftime('%Y%m%d%H%M%S')}{file_extension}"
    if not os.path.exists(os.path.join(directory, original_filename)):
        return original_filename
    else:
        return timestamped_filename

def rename_file_if_exists(old_filename, new_filename):
    """
    Rename an existing file to a new file name.
    :param old_filename: The current file name.
    :param new_filename: The new file name to rename to.
    """
    if old_filename:
        os.rename(old_filename, new_filename)

def ensure_directory_exists(directory):
    """
    Ensure that a directory exists.
    :param directory: The path to the directory to check.
    """
    if not os.path.exists(directory):
        os.makedirs(directory)

def get_output_file_path(directory, filename):
    """
    Construct a file path within the outputs directory, adding a timestamp if the file already exists.
    :param directory: The output directory.
    :param filename: The original file name.
    :return: The full path for the new file to be saved.
    """
    ensure_directory_exists(directory)
    base_filename, file_extension = os.path.splitext(filename)
    timestamped_filename = f"{base_filename}_{datetime.now().strftime('%Y%m%d%H%M%S')}{file_extension}"
    output_filepath = os.path.join(directory, filename)
    timestamped_filepath = os.path.join(directory, timestamped_filename)
    
    return (output_filepath, timestamped_filepath if os.path.exists(output_filepath) else output_filepath)

def rename_and_save_file(src_path, dest_path):
    """
    Rename the source file to the destination path.
    :param src_path: The path to the source file.
    :param dest_path: The path where to save the renamed file.
    """
    if src_path != dest_path:
        os.rename(src_path, dest_path)

def main():
    parser = argparse.ArgumentParser(description='Process and cluster skills.')
    parser.add_argument('--n_clusters', type=int, default=200,
                        help='Number of clusters to divide the skills into.')
    args = parser.parse_args()

    output_directory = "./outputs"
    ensure_directory_exists(output_directory)

    try:
        skills_taxonomy_file = "skills_taxonomy.txt"
        individual_skills_file = "individual_skills.csv"

        # Read skills taxonomy
        skills_list_unique = read_skills_taxonomy(skills_taxonomy_file)
        logging.info(f"Unique skills count: {len(skills_list_unique)}")

        # Cluster skills with the specified number of clusters from the command line
        skill_to_cluster_label = cluster_and_label_skills(skills_list_unique, n_clusters=args.n_clusters)

        # Format and sort the skills taxonomy
        skills_taxonomy = format_and_sort_skills(set(skill_to_cluster_label.values()))

        # Read individual skills data
        df = pd.read_csv(individual_skills_file)

        # Process individual skills
        individual_skills = process_individual_skills(df, skill_to_cluster_label)

        # Generate timestamped filenames if necessary
        skills_taxonomy_filename = get_timestamped_filename(output_directory, "skills_taxonomy_refined.txt")
        individual_skills_filename = get_timestamped_filename(output_directory, "individual_skills_refined.csv")

        # Write refined and sorted skills taxonomy to file in the outputs directory
        write_skills_to_file(skills_taxonomy, os.path.join(output_directory, skills_taxonomy_filename))

        # Create dataframe for individual skills and save to CSV in the outputs directory
        individual_skills_df = pd.DataFrame({
            'Name': individual_skills.keys(),
            'Skills': [', '.join(format_and_sort_skills(skills)) for skills in individual_skills.values()]
        })

        individual_skills_df.to_csv(os.path.join(output_directory, individual_skills_filename), index=False)

    except Exception as e:
        logging.error(f"An error occurred in main: {e}")

if __name__ == '__main__':
    main()
