# st_app.py
import streamlit as st
from utils import extract_skills_from_csv, skills_to_json_list
import pandas as pd

def main():
    st.title("Skills Taxonomy Extractor")

    uploaded_file = st.file_uploader("Upload your CSV", type="csv")
    
    if uploaded_file:
        skills_taxonomy, individual_skills = extract_skills_from_csv(uploaded_file)
        
        st.write("## Skills Taxonomy:")
        for skill in skills_taxonomy:
            st.write(skill)

        st.write("\n## Individual Skills:")
        individual_skills_print = {}
        for name, skills in individual_skills.items():
            individual_skills_print[name] = ', '.join(skills)
        df = pd.DataFrame(list(individual_skills_print.items()), columns=['Name', 'Skills'])
        st.write(df)

if __name__ == "__main__":
    main()
