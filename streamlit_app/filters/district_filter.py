# filters/district_filter.py
import streamlit as st

def apply_district_filter(df):
    options = ["All"] + sorted(df['district_display'].dropna().unique().tolist())
    # Wrap the selectbox in an expander.
    with st.expander("Filter by City Council District", expanded=False):
        selected_district = st.selectbox("Select Council District", options)
    return selected_district
