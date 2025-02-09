# filters/police_district_filter.py
import streamlit as st

def apply_police_district_filter(df):
    options = sorted(df['police_district_sector'].dropna().unique().tolist())
    # Wrap the multiselect in an expander that is collapsed by default.
    with st.expander("Filter by Police Sector - District"):
        selected_options = st.multiselect(
            "Select police sectors",
            options,
            default=options
        )
    return selected_options
