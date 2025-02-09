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

# Set up page configuration
st.set_page_config(page_title="Tacoma 311 Issues Dashboard", layout="wide")

# Read and inject custom CSS
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load data
df = load_issues()
equity_population_df = load_equity_population()
total_population = equity_population_df["population"].sum()

# UI Layout
st.title("Tacoma 311 Issues Dashboard")

# Place filters in the sidebar without an additional expander
with st.sidebar:
    st.header("Filters")
    filtered_df = apply_filters(df)

# Main area: display your visualizations using the filtered DataFrame
display_issues_over_time(filtered_df)
st.markdown("<hr style='border: 1px solid #ccc;'>", unsafe_allow_html=True)
display_aging_analysis(filtered_df)
st.markdown("<hr style='border: 1px solid #ccc;'>", unsafe_allow_html=True)
display_map(filtered_df)
st.markdown("<hr style='border: 1px solid #ccc;'>", unsafe_allow_html=True)
display_issue_summary(filtered_df)
st.markdown("<hr style='border: 1px solid #ccc;'>", unsafe_allow_html=True)
display_assignee_resolution_time(filtered_df)
st.markdown("<hr style='border: 1px solid #ccc;'>", unsafe_allow_html=True)
display_assignee_performance(filtered_df)
st.markdown("<hr style='border: 1px solid #ccc;'>", unsafe_allow_html=True)
issue_data_table(filtered_df)
st.markdown("<hr style='border: 1px solid #ccc;'>", unsafe_allow_html=True)
display_district_resolution_time(filtered_df)
st.markdown("<hr style='border: 1px solid #ccc;'>", unsafe_allow_html=True)
display_equity_issues_analysis(filtered_df, equity_population_df)
st.markdown("<hr style='border: 1px solid #ccc;'>", unsafe_allow_html=True)
display_equity_map(filtered_df)
st.markdown("<hr style='border: 1px solid #ccc;'>", unsafe_allow_html=True)
display_311_impact()
