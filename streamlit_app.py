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
    create_hotspots_map,
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

    st.title("Emerging Hotspots Detection via Geospatial Clustering")

    st.markdown(
        """
        This application uses DBSCAN clustering to identify emerging hotspots based on geospatial data.
        
        **How does it work?**
        
        - **Epsilon (eps):** Controls the maximum distance (in degrees) between two points for them to be considered part of the same cluster.
            - **Lower values:** Only very close points are grouped together, leading to more, smaller clusters.
            - **Higher values:** More distant points are grouped, resulting in larger clusters.
        
        - **Minimum Samples:** Sets the minimum number of points required to form a cluster.
            - **Lower values:** More sensitive to small clusters.
            - **Higher values:** Only groups areas with a higher density of points, filtering out noise.
        
        **Insights:**
        
        - **Hotspot Identification:** Adjusting these parameters helps highlight regions with a high density of points.
        - **Data Sensitivity:** The way clusters form with different parameters can provide insights into the spatial distribution and density of your data.
        - **Anomaly Detection:** Sparse or isolated points that do not form clusters might indicate outliers or anomalies.
        """
    )

    # Place controls for DBSCAN parameters above the map (not in the sidebar)
    eps = st.slider("Epsilon (in degrees)", 0.001, 0.05, 0.005, 0.001)
    min_samples = st.slider("Minimum Samples", 1, 20, 5)

    # Generate the hotspots map using the function
    deck_chart, updated_df = create_hotspots_map(filtered_df, eps, min_samples)
    if deck_chart is not None:
        st.pydeck_chart(deck_chart)
        if 'cluster' in updated_df.columns:
            # Check if 'summary' column exists to show the top value per cluster
            if 'summary' in updated_df.columns:
                # Calculate cluster counts
                cluster_counts = updated_df['cluster'].value_counts().reset_index()
                cluster_counts.columns = ['cluster', 'count']
                
                # Calculate the top (most frequent) summary value for each cluster
                cluster_top_summary = (
                    updated_df.groupby('cluster')['summary']
                    .agg(lambda x: x.value_counts().index[0])
                    .reset_index()
                )
                cluster_top_summary.columns = ['cluster', 'top_summary']
                
                # Merge the two DataFrames to show both counts and top summary values
                cluster_info = pd.merge(cluster_counts, cluster_top_summary, on='cluster', how='left')
                st.write("Cluster Counts with Top Summary:", cluster_info)
            else:
                st.write("Cluster Counts:", updated_df['cluster'].value_counts())
        else:
            st.warning("The 'cluster' column was not found in the updated DataFrame.")
    else:
        st.error("Could not create hotspots map due to errors in the data.")

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
    stats(df)

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