import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go 
from streamlit_js_eval import get_geolocation
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