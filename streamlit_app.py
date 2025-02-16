import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components

# Import data loaders
from streamlit_app.data.load_issues import load_issues  
from streamlit_app.data.load_equity import load_equity_population  

# Import filters and visualizations
from streamlit_app.filters.filters import apply_filters  
from streamlit_app.visuals import (
    heads_up,
    display_map,
    council_districts,
    display_department_performance,
    display_issues_over_time,
    display_issue_summary,
    display_aging_analysis,
    display_assignee_resolution_time,
    display_assignee_performance,
    display_equity_issues_analysis,
    display_equity_map,
    display_311_impact,
    issue_data_table,
    stats,
)


GA_TRACKING_ID = "G-T8DYCYF3YN"

html_code = f"""
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id={GA_TRACKING_ID}"></script>
<script>
window.dataLayer = window.dataLayer || [];
function gtag(){{dataLayer.push(arguments);}}
gtag('js', new Date());
gtag('config', '{GA_TRACKING_ID}');
</script>
"""

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

with st.sidebar:
    st.header("Filters")
    filtered_df = apply_filters(df)

# Define the tab labels
tab_labels = [
    "Issue Overview",
    "Issues Over Time",
    "Aging Analysis",
    "Map",
    "City Council Districts",
    "Department Performance",
    "Issue Summary",
    "Assignee Resolution Time",
    "Assignee Performance",
    "Equity Issues Analysis",
    "Equity Map",
    "Data Table",
    "311 Impact",
    "Data Details"
]

tabs = st.tabs(tab_labels)

components.html(html_code, height=0)

with tabs[0]:
    heads_up(filtered_df)

with tabs[1]:
    display_issues_over_time(filtered_df)

with tabs[2]:
    display_aging_analysis(filtered_df)

with tabs[3]:
    display_map(filtered_df)

with tabs[4]:
    council_districts(filtered_df)

with tabs[5]:
    display_department_performance(filtered_df)

with tabs[6]:
    display_issue_summary(filtered_df)

with tabs[7]:
    display_assignee_resolution_time(filtered_df)

with tabs[8]:
    display_assignee_performance(filtered_df)

with tabs[9]:
    display_equity_issues_analysis(filtered_df, equity_population_df)

with tabs[10]:
    display_equity_map(filtered_df)

with tabs[11]:
    issue_data_table(filtered_df)

with tabs[12]:
    display_311_impact()

with tabs[13]:
    # stats(df)

    st.markdown(
        """
        This tool is built based on a GitHub repo that anyone can replicate.

        https://github.com/jseek/seeclickfix_tacoma_data/

        This package uses Airflow to pull data from Tacoma's 311 system, stores the data in a parquet file, and serves it through Streamlit for visuaization.


        """,
        unsafe_allow_html=True
    )


    st.header("DataFrame Description")
    
    # Display column names
    st.subheader("Column Names")
    st.write(df.columns.tolist())
    
    # Display summary statistics (including non-numeric columns)
    st.subheader("Summary Statistics")
    st.write(df.describe(include='all'))
    
    # Display data types for each column
    st.subheader("Data Types")
    st.write(df.dtypes)
    
    # Optionally, display a sample of the data
    st.subheader("Data Preview")
    st.dataframe(df.head())