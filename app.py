# st_app.py
import streamlit as st
from utils import extract_skills_from_csv, extract_skills_from_csv_in_realtime
import pandas as pd
import io

def main():
    st.title("Skills Taxonomy Extractor")

    uploaded_file = st.file_uploader("Upload your CSV", type="csv")

    if uploaded_file:
        skills_taxonomy, individual_skills = extract_skills_from_csv_in_realtime(uploaded_file)

        st.write("## Skills Taxonomy:")
        for skill in skills_taxonomy:
            st.write(skill)

        st.write("\n## Individual Skills:")

        # Convert DataFrame to a CSV in memory
        buf = io.StringIO()
        df = pd.DataFrame(list(individual_skills.items()), columns=['Name', 'Skills'])
        df.to_csv(buf, index=False)
        csv_data = buf.getvalue()

        # Provide download button for the CSV
        st.download_button(
            label="Download Processed Data as CSV",
            data=csv_data,
            file_name="processed_data.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()
