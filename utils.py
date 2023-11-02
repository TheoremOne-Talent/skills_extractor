import pandas as pd
import openai
import json
import os
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
    """
    Extract skills from a CSV file using OpenAI API.

    Args:
        csv_path (str): Path to the CSV file.

    Returns:
        set: Skills taxonomy.
        dict: Individual skills.
    """
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"File not found: {csv_path}")
        return set(), {}

    skills_taxonomy = set()
    individual_skills = {}

    for index, row in df.iterrows():
        skills = call_openai_api(row['Skill Sets'])
        skills_taxonomy.update(skills)
        individual_skills[row['Name']] = skills

    return skills_taxonomy, individual_skills


def main():
    csv_path = "skills.csv"  # Replace with the path to your CSV

    skills_taxonomy, individual_skills = extract_skills_from_csv(csv_path)

    print("Skills Taxonomy:")
    for skill in skills_taxonomy:
        print(skill)

    print("\nIndividual Skills:")
    for name, skills in individual_skills.items():
        print(f"{name}: {', '.join(skills)}")


if __name__ == "__main__":
    main()
