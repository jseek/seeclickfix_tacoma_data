import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Import data loaders
from streamlit_app.data.load_issues import load_issues  
from streamlit_app.data.load_equity import load_equity_population  

# Import filters and visualizations
from streamlit_app.filters.filters import apply_filters  
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

# Set up page configuration (sidebar expanded by default)
st.set_page_config(
    page_title="Tacoma 311 Issues Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Read and inject custom CSS (if desired)
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Optional: Add a persistent "Filters" label on the main page
st.markdown(
    """
    <style>
    .fixed-filter-label {
        position: fixed;
        top: 10px;
        left: 10px;
        background-color: #f0f2f6;
        padding: 5px 10px;
        border-radius: 4px;
        font-weight: bold;
        z-index: 1000;
    }
    </style>
    <div class="fixed-filter-label">Filters</div>
    """,
    unsafe_allow_html=True,
)

# Load data
df = load_issues()
equity_population_df = load_equity_population()
total_population = equity_population_df["population"].sum()

# UI Layout
st.title("Tacoma 311 Issues Dashboard")

with st.sidebar:
    st.sidebar.title("Filters")
    filtered_df = apply_filters(df)

# Define the tab labels
tab_labels = [
    "Issues Over Time",
    "Aging Analysis",
    "Map",
    "Issue Summary",
    "Assignee Resolution Time",
    "Assignee Performance",
    "District Resolution Time",
    "Equity Issues Analysis",
    "Equity Map",
    "Data Table",
    "311 Impact"
]

tabs = st.tabs(tab_labels)

with tabs[0]:
    display_issues_over_time(filtered_df)

with tabs[1]:
    display_aging_analysis(filtered_df)

with tabs[2]:
    display_map(filtered_df)

with tabs[3]:
    display_issue_summary(filtered_df)

with tabs[4]:
    display_assignee_resolution_time(filtered_df)

with tabs[5]:
    display_assignee_performance(filtered_df)

with tabs[6]:
    display_district_resolution_time(filtered_df)

with tabs[7]:
    display_equity_issues_analysis(filtered_df, equity_population_df)

with tabs[8]:
    display_equity_map(filtered_df)

with tabs[9]:
    issue_data_table(filtered_df)

with tabs[10]:
    display_311_impact()