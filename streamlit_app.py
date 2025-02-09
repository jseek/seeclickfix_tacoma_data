import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Import data loaders
from streamlit_app.data.load_issues import load_issues  
from streamlit_app.data.load_equity import load_equity_population  

from streamlit_app.filters.filters import apply_filters  

# Import visualizations
from streamlit_app.visuals import (
    display_map,
    display_issues_over_time,
    display_issue_summary,
    display_aging_analysis,
    display_assignee_resolution_time,
    display_assignee_performance,
    display_district_resolution_time,
    display_equity_issues_analysis,
    display_equity_map,
    display_311_impact,
    issue_data_table,
)

st.set_page_config(page_title="Tacoma 311 Issues Dashboard", layout="wide")

# Load data
df = load_issues()
equity_population_df = load_equity_population()

# Calculate total population across all areas
total_population = equity_population_df["population"].sum()

# UI Layout
st.title("Tacoma 311 Issues Dashboard")

# Wrap the filters in a single collapsible expander.
with st.expander("Show / Hide Filters", expanded=False):
    filtered_df = apply_filters(df)

# Now use the filtered dataframe for your visualizations
display_issues_over_time(filtered_df)

# Aging Analysis section
st.markdown("<hr style='border: 1px solid #ccc;'>", unsafe_allow_html=True)
display_aging_analysis(filtered_df)

# Location Analysis section
st.markdown("<hr style='border: 1px solid #ccc;'>", unsafe_allow_html=True)
display_map(filtered_df)

# Issue Summary section
st.markdown("<hr style='border: 1px solid #ccc;'>", unsafe_allow_html=True)
display_issue_summary(filtered_df)

# Assignee resolution time section
st.markdown("<hr style='border: 1px solid #ccc;'>", unsafe_allow_html=True)
display_assignee_resolution_time(filtered_df)

# Assignee performance section
st.markdown("<hr style='border: 1px solid #ccc;'>", unsafe_allow_html=True)
display_assignee_performance(filtered_df)

# Issue data table section
st.markdown("<hr style='border: 1px solid #ccc;'>", unsafe_allow_html=True)
issue_data_table(filtered_df)

# District resolution time section
st.markdown("<hr style='border: 1px solid #ccc;'>", unsafe_allow_html=True)
display_district_resolution_time(filtered_df)

# Equity Analysis Section
st.markdown("<hr style='border: 1px solid #ccc;'>", unsafe_allow_html=True)
display_equity_issues_analysis(filtered_df, equity_population_df)

# Equity Map Section
st.markdown("<hr style='border: 1px solid #ccc;'>", unsafe_allow_html=True)
display_equity_map(filtered_df)

# Impact section
st.markdown("<hr style='border: 1px solid #ccc;'>", unsafe_allow_html=True)
display_311_impact()
