# st_app.py
import streamlit as st
from utils import extract_skills_from_csv, extract_skills_from_csv_in_realtime
import pandas as pd
import io

def main():
    st.title("Skills Taxonomy Extractor")

    uploaded_file = st.file_uploader("Upload your CSV", type="csv")

    # Check if 'processed' state exists in session state, if not, initialize it to False
    if 'processed' not in st.session_state:
        st.session_state.processed = False

    # If a new file is uploaded, process the data and set the 'processed' state to True
    if uploaded_file and not st.session_state.processed:
        skills_taxonomy, current_df = extract_skills_from_csv_in_realtime(uploaded_file)

        st.session_state.skills_taxonomy = skills_taxonomy
        st.session_state.current_df = current_df

        st.session_state.processed = True

    # If the data has been processed, display the results and download button
    if st.session_state.processed:
        st.write("## Skills Taxonomy:")
        for skill in st.session_state.skills_taxonomy:
            st.write(skill)

        st.write("\n## Individual Skills:")

        # Convert DataFrame to a CSV in memory
        buf = io.StringIO()
        st.session_state.current_df.to_csv(buf, index=False)
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
