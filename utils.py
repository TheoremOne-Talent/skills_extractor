import pandas as pd
import openai
import json
import os
import streamlit as st
from cluster_skills import cluster_skills
import warnings
warnings.filterwarnings("ignore")

from dotenv import load_dotenv
load_dotenv()

# Read the API key from an environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

def skills_to_json_list(*skills):
    """
    Convert skills into a JSON-encoded list.

    Args:
        *skills: Variable arguments of skill strings.

    Returns:
        str: A JSON-encoded string representing the list of skills.
    """
    return json.dumps(list(skills))


def call_openai_api(skills_text):
    """
    Make an API call to OpenAI to process the skills text.

    Args:
        skills_text (str): Text containing skills.

    Returns:
        list: Extracted skills from the text.
    """
    functions = [
        {
            "name": "skills_to_json_list",
            "description": "Convert a variable number of skills into a JSON-encoded list.",
            "parameters": {
                "type": "object",
                "properties": {
                    "skills": {
                        "type": "array",
                        "description": "A variable number of skill strings.",
                        "items": {
                            "type": "string"
                        }
                    }
                },
                "required": ["skills"]
            }
        }
    ]

    try:
        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=[{'role': 'user', 'content': skills_text}],
            functions=functions,
            function_call={"name": "skills_to_json_list"}
        )
        arguments = json.loads(response["choices"][0]["message"]["function_call"]["arguments"])
        return arguments["skills"]
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return []

def extract_skills_from_csv(csv_path):
    # Read the CSV
    df = pd.read_csv(csv_path)
    # df = df.head(6)  # For demonstration, take only the first 5 rows

    print(f"Initial DataFrame:\n{df}\n")  # Debugging print

    raw_skills = set()
    individual_skills = {}
    skills_taxonomy = set()

    for _, row in df.iterrows():
        skills = call_openai_api(row['Skill Sets'])
        print(f"Skills for {row['Name']}: {skills}")  # Debugging print

        raw_skills.update(skills)
        individual_skills[row['Name']] = skills

        # Update individual_skills.csv in real-time
        individual_skills_df = pd.DataFrame({
            'Name': individual_skills.keys(),
            'Skills': [', '.join(skills) for skills in individual_skills.values()]
        })
        individual_skills_df.to_csv("individual_skills.csv", index=False)

    # Cluster skills after gathering all of them
    skills_list = list(raw_skills)
    print(f"Total unique skills gathered: {len(skills_list)}")
    clusters = cluster_skills(skills_list)

    skill_to_cluster_label = {skill: cluster_name for cluster_name, skills in clusters for skill in skills}
    
    # Update the skills_taxonomy
    skills_taxonomy = set(skill_to_cluster_label.values())

    # Write to skills_taxonomy.txt
    with open("skills_taxonomy.txt", "w") as f:
        for skill in skills_taxonomy:
            f.write(skill + "\n")

    # Update individual_skills with the clustered skills names
    for name, skills in individual_skills.items():
        clustered_skills = [skill_to_cluster_label.get(skill, skill) for skill in skills]
        individual_skills[name] = list(set(clustered_skills))  # Remove duplicates

    return skills_taxonomy, individual_skills

def extract_skills_from_csv_in_realtime(uploaded_file):
    # Read the entire CSV
    df = pd.read_csv(uploaded_file)

    raw_skills = set()
    
    # Create a placeholder dataframe and placeholder for the table
    current_df = pd.DataFrame(columns=['Name', 'Skills'])
    table_placeholder = st.empty()
    
    # df = df.head(6)  # For demonstration, take only the first 5 rows
    
    # Initialize progress bar and status text
    progress_bar = st.progress(0)
    status_text = st.empty()
    total_rows = len(df)
    
    # Process row-by-row
    for index, row in df.iterrows():
        skills = call_openai_api(row['Skill Sets'])
        raw_skills.update(skills)
        
        # Cluster skills immediately
        skills_list = list(raw_skills)
        clusters = cluster_skills(skills_list)
        skill_to_cluster_label = {skill: cluster_name for cluster_name, skills in clusters for skill in skills}
        clustered_skills = [skill_to_cluster_label.get(skill, skill) for skill in skills]
        skills_str = ', '.join(set(clustered_skills))
        
        # Add the processed data to current_df and display the table
        current_df.loc[index] = [row['Name'], skills_str]
        table_placeholder.table(current_df)
        
        # Update progress bar and status text
        progress = (index + 1) / total_rows
        progress_bar.progress(progress)
        status_text.text(f"Processing row {index + 1} of {total_rows}...")

    # Update skills_taxonomy to only consist of the cluster names
    skills_taxonomy = set(skill_to_cluster_label.values())
    
    # Clear status text
    status_text.text(f"Processed {total_rows} rows!")
    
    return skills_taxonomy, current_df


def main():
    csv_path = "skills.csv"  # Replace with the path to your CSV

    skills_taxonomy, individual_skills = extract_skills_from_csv(csv_path)

    print("Skills Taxonomy:")
    for skill in skills_taxonomy:
        print(skill)

    print("\nIndividual Skills:")
    for name, skills in individual_skills.items():
        print(f"{name}: {', '.join(skills)}")

    # Save skills_taxonomy in a .txt file
    with open("skills_taxonomy.txt", "w") as f:
        for skill in skills_taxonomy:
            f.write(skill + "\n")

    # Save individual_skills in a .csv file
    individual_skills_df = pd.DataFrame({
        'Name': individual_skills.keys(),
        'Skills': [', '.join(skills) for skills in individual_skills.values()]
    })
    individual_skills_df.to_csv("individual_skills.csv", index=False)


if __name__ == "__main__":
    main()
