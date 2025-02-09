# filters/issue_type_filter.py
import streamlit as st

def apply_issue_type_filter(df):
    with st.expander("Issue Type", expanded=False):
        options = df['summary'].unique().tolist()
        selected = st.multiselect("Select Summaries", options, default=options)
    return selected
