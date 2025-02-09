import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_app.visuals.issue_mapping import display_map
from streamlit_app.visuals.issues_over_time import display_issues_over_time
from streamlit_app.visuals.issue_summary_chart import display_issue_summary
from streamlit_app.visuals.aging_analysis import display_aging_analysis
from streamlit_app.visuals.assignee_resolution_time import display_assignee_resolution_time
from streamlit_app.visuals.assignee_performance import display_assignee_performance
from streamlit_app.visuals.district_resolution_time import display_district_resolution_time
from streamlit_app.visuals.equity_issues_analysis import display_equity_issues_analysis
from streamlit_app.visuals.equity_map import display_equity_map
from streamlit_app.visuals.about_311_impact import display_311_impact
from streamlit_app.filters.filters import apply_filters
from streamlit_app.data.load_issues import load_issues  # Import issues data loader
from streamlit_app.data.load_equity import load_equity_population  # Import equity data loader

st.set_page_config(page_title="Tacoma 311 Issues Dashboard", layout="wide")

# Load data
df = load_issues()
equity_population_df = load_equity_population()

# Calculate total population across all areas
total_population = equity_population_df["population"].sum()

# UI Layout
st.title("Tacoma 311 Issues Dashboard")

# Apply filters and get the filtered dataframe & second column for charts
filtered_df, col2 = apply_filters(df)

# Use col2 for displaying visualizations
with col2:
    display_issues_over_time(filtered_df)

# Aging Analysis section
st.markdown("<hr style='border: 1px solid #ccc;'>", unsafe_allow_html=True)
display_aging_analysis(filtered_df)

## Location Analysis section
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
st.subheader("Issue Data Table")
st.markdown("Details on each issue.")
st.dataframe(filtered_df)

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
