import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
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

# Set page config to use wide layout
st.set_page_config(page_title="Tacoma 311 Issues Dashboard", layout="wide")

# Load data from Parquet file - caches data for efficiency
@st.cache_data
def load_data():
    df = pd.read_parquet("exports/seeclickfix_issues_dump.parquet")
    df['created_at'] = pd.to_datetime(df['created_at'])

    show_issues_after_date = '2024-01-01'
    df = df[df['created_at'] >= show_issues_after_date]

    df['updated_at'] = pd.to_datetime(df['updated_at'])
    df['acknowledged_at'] = pd.to_datetime(df['acknowledged_at'])
    df['closed_at'] = pd.to_datetime(df['closed_at'])

    df['homeless_related'] = df['summary'].str.contains("homeless|someone living on", case=False, na=False) | \
                            df['description'].str.contains("homeless", case=False, na=False)

    df['homeless_related'] = df['homeless_related'].map({True: 'homeless-related', False: 'other issues'})

    # Create formatted district display
    df['district_display'] = df['council_district'].fillna(0).astype(int).astype(str) + " - " + df['councilmember'].fillna("Unknown")
    
    # Create formatted police district-sector display
    df['police_district_sector'] = df['police_sector'].astype(str) + " - " + df['police_district'].astype(str)

    # Fill missing values for shelter-related fields
    df['within_10_blocks_of_shelter'] = df['within_10_blocks_of_shelter'].fillna(False)
    
    return df

# Load equity population data from GeoJSON
@st.cache_data
def load_equity_population():
    with open("exports/Equity_Index_2024_(Tacoma).geojson", "r", encoding="utf-8") as f:
        data = json.load(f)

    equity_population_df = pd.DataFrame([
        {
            "equity_objectid": feature["properties"].get("objectid"),
            "population": feature["properties"].get("population", 0)  # Default to 0 if missing
        }
        for feature in data["features"]
    ])
    
    return equity_population_df

# Load data
df = load_data()
equity_population_df = load_equity_population()

# Calculate total population across all areas
total_population = equity_population_df["population"].sum()

# UI Layout
st.title("Tacoma 311 Issues Dashboard")

col1, col2 = st.columns([1, 2])

with col1:
    min_date, max_date = df['created_at'].min().to_pydatetime(), df['created_at'].max().to_pydatetime()
    date_range = st.slider("Select Issue Created Date Range", min_value=min_date, max_value=max_date, value=(min_date, max_date))

    # District filter
    district_options = ["All"] + sorted(df['district_display'].dropna().unique().tolist())
    selected_district = st.selectbox("Filter by City Council District", district_options)
    
    # Police district-sector filter
    police_district_sector_options = sorted(df['police_district_sector'].dropna().unique().tolist())
    with st.expander("Filter by Police Sector - District", expanded=False):
        selected_police_district_sectors = st.multiselect(
            "Select Police Sectors",
            police_district_sector_options,
            default=police_district_sector_options
        )

    # Equity Index filter
    equity_index_options = ["All"] + sorted(df['equityindex'].dropna().unique().tolist())
    selected_equity_index = st.selectbox("Filter by Equity Index", equity_index_options)

    st.markdown("Issue Type")
    summary_options = df['summary'].unique().tolist()

    with st.expander("Expand to select issue types"):
        selected_summaries = st.multiselect("Select Summaries", summary_options, default=summary_options)
    
    homeless_toggle = st.toggle("Show only homeless-related issues", value=False)

    # Shelter Proximity Filters
    shelter_toggle = st.toggle("Show only issues within 10 blocks of a shelter", value=False)

# Apply filters
filtered_df = df[(df['created_at'] >= date_range[0]) & (df['created_at'] <= date_range[1])]

if selected_district != "All":
    filtered_df = filtered_df[filtered_df['district_display'] == selected_district]

if selected_police_district_sectors:
    filtered_df = filtered_df[filtered_df['police_district_sector'].isin(selected_police_district_sectors)]

if selected_equity_index != "All":
    filtered_df = filtered_df[filtered_df['equityindex'] == selected_equity_index]

if homeless_toggle:
    filtered_df = filtered_df[filtered_df['homeless_related'] == 'homeless-related']

filtered_df = filtered_df[filtered_df['summary'].isin(selected_summaries)]

# Apply shelter-related filters
if shelter_toggle:
    filtered_df = filtered_df[filtered_df['within_10_blocks_of_shelter'] == True]

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

# assignee resolution time section
st.markdown("<hr style='border: 1px solid #ccc;'>", unsafe_allow_html=True)
display_assignee_resolution_time(filtered_df)

# assignee performance section
st.markdown("<hr style='border: 1px solid #ccc;'>", unsafe_allow_html=True)
display_assignee_performance(filtered_df)

st.markdown("<hr style='border: 1px solid #ccc;'>", unsafe_allow_html=True)
# issue data table section
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