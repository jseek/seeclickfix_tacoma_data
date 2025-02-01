import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Database connection function - caches the connection to prevent repeated calls
@st.cache_resource
def get_connection():
    return psycopg2.connect(
        dbname="airflow",
        user="airflow",
        password="airflow",
        host="postgres",
        port="5432"
    )

# Load data from PostgreSQL - caches data for efficiency
@st.cache_data
def load_data():
    conn = get_connection()
    query = """
        SELECT
            id, description, status, created_at, updated_at, acknowledged_at, closed_at,
            lat, lng, vote_count, comment_count, rating, summary, request_type_title, assignee_name,
            CASE
                WHEN summary ILIKE '%homeless%'
                    OR summary ILIKE '%someone%living%on%%' THEN 'homeless-related'
                ELSE 'other issues'
            END AS homeless_related
        FROM seeclickfix_issues
    """
    df = pd.read_sql(query, conn)  # Load data from SQL query into a DataFrame
    conn.close()  # Close the connection after fetching data
    return df

# Streamlit UI setup
st.title("Tacoma 311 Issues Dashboard")
st.markdown("📊 Interactive analysis of reported issues in Tacoma.")

# Load data
df = load_data()

# Add date filter slider
st.subheader("Filter by Date")
min_date, max_date = pd.to_datetime(df['created_at']).min(), pd.to_datetime(df['created_at']).max()
date_range = st.slider("Select Date Range", min_value=min_date.to_pydatetime(), max_value=max_date.to_pydatetime(), value=(min_date.to_pydatetime(), max_date.to_pydatetime()))
filtered_df = df[(df['created_at'] >= date_range[0]) & (df['created_at'] <= date_range[1])]

# Arrange filters in columns
col1, col2 = st.columns(2)

with col1:
    st.subheader("Filter by Homeless-Related Issues")
    homeless_toggle = st.toggle("Show only homeless-related issues", value=False)

# Apply the filter if the toggle is enabled
if homeless_toggle:
    filtered_df = filtered_df[filtered_df['homeless_related'] == 'homeless-related']

with col2:
    st.subheader("Filter by Issue Type")
    st.markdown("Expand the section below to select issue types.")
    summary_options = df['summary'].unique().tolist()
    with st.expander("Expand to select issue types"):
        selected_summaries = st.multiselect("Select Summaries", summary_options, default=summary_options)
    filtered_df = filtered_df[filtered_df['summary'].isin(selected_summaries)]

# Display issue summary statistics
st.subheader("311 Issue Summary")
st.write(f"Total Issues: **{len(filtered_df)}**")
st.write(f"Open Issues: **{len(filtered_df[filtered_df['status'] != 'Closed'])}**")
st.write(f"Closed Issues: **{len(filtered_df[filtered_df['status'] == 'Closed'])}**")

# Compute aging analysis
st.subheader("Aging Analysis")
st.markdown("For issues that have not been closed, shows the median time to acknowledge an issue, the count of acknowledged issues, and the percentage of issues that have been acknowledged, grouped by the kind of issue.")
aging_df = filtered_df[filtered_df['status'].isin(["Open", "Acknowledged"])].copy()
aging_df['resolved_at'] = aging_df[['acknowledged_at', 'closed_at']].min(axis=1)
aging_df['days_to_resolution'] = (aging_df['resolved_at'] - aging_df['created_at']).dt.days
aging_df['days_to_acknowledge'] = (aging_df['acknowledged_at'] - aging_df['created_at']).dt.days
aging_df['acknowledged'] = aging_df['acknowledged_at'].notna()

aging_summary = aging_df.groupby('summary').agg(
    median_days_to_acknowledge=('days_to_acknowledge', 'median'),
    count_acknowledged=('acknowledged', 'sum'),
    issue_count=('summary', 'count')
).reset_index()

aging_summary['percent_acknowledged'] = (aging_summary['count_acknowledged'] / aging_summary['issue_count']) * 100
aging_summary = aging_summary.sort_values(by='issue_count', ascending=False)

st.dataframe(aging_summary)

# Time series visualization of issues over time
st.subheader("Issues Over Time (Weekly)")
st.markdown("Number of issues created each week")
filtered_df['week'] = filtered_df['created_at'].dt.to_period('W').apply(lambda r: r.start_time)  # Convert to week start date
time_series = filtered_df.groupby(filtered_df['week']).count()['id']  # Count issues per week
st.line_chart(time_series)

# Display issue locations on a map
st.subheader("Issue Locations")
st.markdown("Maps the geographical distribution of issues. Hover over the dot for details on the issue.")
fig = px.scatter_mapbox(filtered_df, lat="lat", lon="lng", hover_data=["description", "status"],
                         mapbox_style="open-street-map", zoom=10)
st.plotly_chart(fig)

# Heatmap of issue density
st.subheader("Issue Heatmap")
st.markdown("Highlights areas with a high concentration of reported issues.")
fig_heatmap = go.Figure(go.Densitymapbox(
    lat=filtered_df['lat'],
    lon=filtered_df['lng'],
    z=[1] * len(filtered_df),  # Each point contributes equally
    radius=10,  # Adjust radius for heat intensity
    colorscale="Viridis"
))
fig_heatmap.update_layout(
    mapbox_style="open-street-map",
    mapbox_center={"lat": filtered_df['lat'].mean(), "lon": filtered_df['lng'].mean()},
    mapbox_zoom=10
)
st.plotly_chart(fig_heatmap)

# Horizontal bar chart for issue summary counts
st.subheader("Issues by Type")
st.markdown("Shows the most reported issues.")
summary_counts = filtered_df['summary'].value_counts().sort_values(ascending=True)  # Sort by count
fig_bar = px.bar(summary_counts, x=summary_counts.values, y=summary_counts.index, 
                 orientation='h', labels={'x': 'Count', 'y': 'Request Type'})
st.plotly_chart(fig_bar)

# Pie chart for categorizing issues as homeless-related or other
st.subheader("Homeless-Related Issues")
homeless_counts = filtered_df['homeless_related'].value_counts()
fig_pie = px.pie(names=homeless_counts.index, values=homeless_counts.values, 
                 title="Proportion of Homeless-Related Issues")
st.plotly_chart(fig_pie)

# Display a filterable table of issue data
st.subheader("Issue Data Table")
st.markdown("Details on each issue.")
st.dataframe(filtered_df)

# Chronic Issue Areas (Grouped by Quarter Mile - Top 10%)
st.subheader("Chronic Issue Areas")
st.markdown("Groups repeated reports into quarter-mile areas and highlights the top 10% most reported locations.")

def group_issues_by_quarter_mile(filtered_df, resolution=0.004):
    filtered_df['lat_round'] = (filtered_df['lat'] / resolution).round() * resolution
    filtered_df['lng_round'] = (filtered_df['lng'] / resolution).round() * resolution
    grouped_df = filtered_df.groupby(['lat_round', 'lng_round']).size().reset_index(name='count')
    return grouped_df

chronic_issues = group_issues_by_quarter_mile(filtered_df)
threshold = chronic_issues['count'].quantile(0.90)  # Top 10% cutoff
chronic_issues_top = chronic_issues[chronic_issues['count'] >= threshold]
fig_chronic = px.scatter_mapbox(chronic_issues_top, lat='lat_round', lon='lng_round', size='count',
                                mapbox_style='open-street-map', zoom=10,
                                title="Top 10% Quarter-Mile Grouped Chronic Issue Locations")
st.plotly_chart(fig_chronic)