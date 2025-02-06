import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Set page config to use wide layout
st.set_page_config(page_title="Tacoma 311 Issues Dashboard", layout="wide")

# Load data from JSON file - caches data for efficiency
@st.cache_data
def load_data():
    df = pd.read_json("exports/seeclickfix_issues_dump.json")
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['updated_at'] = pd.to_datetime(df['updated_at'])
    df['acknowledged_at'] = pd.to_datetime(df['acknowledged_at'])
    df['closed_at'] = pd.to_datetime(df['closed_at'])

    df['homeless_related'] = df['summary'].str.contains("homeless|someone living on", case=False, na=False) | \
                            df['description'].str.contains("homeless", case=False, na=False)

    df['homeless_related'] = df['homeless_related'].map({True: 'homeless-related', False: 'other issues'})


    return df

# Streamlit UI setup
st.title("Tacoma 311 Issues Dashboard")

# Load data
df = load_data()

col1, col2 = st.columns([1, 2])

with col1:
    min_date, max_date = df['created_at'].min().to_pydatetime(), df['created_at'].max().to_pydatetime()
    date_range = st.slider("Select Issue Created Date Range", min_value=min_date, max_value=max_date, value=(min_date, max_date))


    st.markdown("Issue Type")
    summary_options = df['summary'].unique().tolist()

    with st.expander("Expand to select issue types"):
        selected_summaries = st.multiselect("Select Summaries", summary_options, default=summary_options)
    homeless_toggle = st.toggle("Show only homeless-related issues", value=False)

# Apply filters
filtered_df = df[(df['created_at'] >= date_range[0]) & (df['created_at'] <= date_range[1])]

if homeless_toggle:
    filtered_df = filtered_df[filtered_df['homeless_related'] == 'homeless-related']

filtered_df = filtered_df[filtered_df['summary'].isin(selected_summaries)]

with col2:
    st.write(f"**Issue Summary:**  Total Issues: **{len(filtered_df)}** | Open Issues: **{len(filtered_df[filtered_df['status'] != 'Closed'])}** | Closed Issues: **{len(filtered_df[filtered_df['status'] == 'Closed'])}**")

    st.subheader("Issues Over Time (Weekly)")
    st.markdown("Number of issues created each week")
    filtered_df['week'] = filtered_df['created_at'].dt.to_period('W').apply(lambda r: r.start_time)  # Convert to week start date
    time_series = filtered_df.groupby(filtered_df['week']).count()['id']  # Count issues per week
    st.line_chart(time_series)

st.markdown("<hr style='border: 1px solid #ccc;'>", unsafe_allow_html=True)

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

## Location Analysis section
st.markdown("<hr style='border: 1px solid #ccc;'>", unsafe_allow_html=True)

map_col1, map_col2 = st.columns([1, 1])
issue_mapping_df = filtered_df

with map_col1:
    # Display issue locations on a map
    st.subheader("Issue Locations")
    st.markdown("Maps the geographical distribution of issues. Hover over the dot for details on the issue.")
    fig = px.scatter_mapbox(issue_mapping_df, lat="lat", lon="lng", hover_data=["description", "status"],
                            mapbox_style="open-street-map", zoom=10)
    st.plotly_chart(fig)

with map_col2:
    # Heatmap of issue density
    st.subheader("Issue Heatmap")
    st.markdown("Highlights areas with a high concentration of reported issues.")
    fig_heatmap = go.Figure(go.Densitymapbox(
        lat=issue_mapping_df['lat'],
        lon=issue_mapping_df['lng'],
        z=[1] * len(issue_mapping_df),  # Each point contributes equally
        radius=10,  # Adjust radius for heat intensity
        colorscale="Viridis"
    ))
    fig_heatmap.update_layout(
        mapbox_style="open-street-map",
        mapbox_center={"lat": issue_mapping_df['lat'].mean(), "lon": issue_mapping_df['lng'].mean()},
        mapbox_zoom=10
    )
    st.plotly_chart(fig_heatmap)


st.markdown("<hr style='border: 1px solid #ccc;'>", unsafe_allow_html=True)

# Horizontal bar chart for issue summary counts
st.subheader("Issues by Type")
st.markdown("Shows the most reported issues.")
summary_counts = filtered_df['summary'].value_counts().sort_values(ascending=True)  # Sort by count
fig_bar = px.bar(summary_counts, x=summary_counts.values, y=summary_counts.index, 
                 orientation='h', labels={'x': 'Count', 'y': 'Request Type'})
st.plotly_chart(fig_bar)

# Compute resolution time
filtered_df['resolved_at'] = filtered_df[['acknowledged_at', 'closed_at']].min(axis=1)
filtered_df['time_to_resolution'] = (filtered_df['resolved_at'] - filtered_df['created_at']).dt.days

st.markdown("<hr style='border: 1px solid #ccc;'>", unsafe_allow_html=True)

st.subheader("Issue Resolution Time by Assignee")
st.markdown("Each point represents an assignee, showing the total number of issues assigned to them and the average time taken to acknowledge or close the issue.")
assignee_stats = filtered_df.groupby('assignee_name').agg(
    num_issues=('id', 'count'),
    avg_time_to_resolution=('time_to_resolution', 'mean')
).reset_index()
fig_scatter = px.scatter(
    assignee_stats, x='num_issues', y='avg_time_to_resolution',
    hover_data=['assignee_name'], labels={'num_issues': 'Number of Issues', 'avg_time_to_resolution': 'Avg Time to Resolution (days)'},
    title='Resolution Time vs. Number of Issues by Assignee'
)
st.plotly_chart(fig_scatter)

st.markdown("<hr style='border: 1px solid #ccc;'>", unsafe_allow_html=True)

# Compute assignee performance statistics
filtered_df['time_to_acknowledge'] = (filtered_df['acknowledged_at'] - filtered_df['created_at']).dt.days
filtered_df['time_to_close'] = (filtered_df['closed_at'] - filtered_df['created_at']).dt.days

# Aggregate issue counts and response times per assignee
assignee_stats = filtered_df.groupby('assignee_name').agg(
    total_issues=('id', 'count'),
    acknowledged_issues=('acknowledged_at', 'count'),
    closed_issues=('closed_at', 'count'),
    avg_time_to_acknowledge=('time_to_acknowledge', 'mean'),
    avg_time_to_close=('time_to_close', 'mean')
).reset_index()

# Compute acknowledgment and closure rates
assignee_stats['acknowledgment_rate'] = (assignee_stats['acknowledged_issues'] / assignee_stats['total_issues']) * 100
assignee_stats['closure_rate'] = (assignee_stats['closed_issues'] / assignee_stats['total_issues']) * 100

# Determine the top summary per assignee based on issue count
top_summary = (
    filtered_df.groupby(['assignee_name', 'summary'])
    .size()
    .reset_index(name='summary_count')
    .sort_values(['assignee_name', 'summary_count'], ascending=[True, False])
    .drop_duplicates(subset=['assignee_name'], keep='first')
    .rename(columns={'summary': 'top_issue_type'})
)

# Merge the top summary back into assignee_stats
assignee_stats = assignee_stats.merge(top_summary[['assignee_name', 'top_issue_type']], on='assignee_name', how='left')

# Sort the final DataFrame by issue count in descending order
assignee_stats = assignee_stats.sort_values(by='total_issues', ascending=False)

# Display results
st.subheader("Assignee Performance Summary")
st.dataframe(assignee_stats)

st.markdown("<hr style='border: 1px solid #ccc;'>", unsafe_allow_html=True)

# Display a filterable table of issue data
st.subheader("Issue Data Table")
st.markdown("Details on each issue.")
st.dataframe(filtered_df)

st.markdown("<hr style='border: 1px solid #ccc;'>", unsafe_allow_html=True)


st.markdown(
    """
    Tacoma’s 311 system serves as a critical channel for residents to report non-emergency issues, such as potholes, graffiti, illegal dumping, and homelessness-related concerns. Effectively tracking and analyzing these reports is essential for improving city services, increasing government accountability, and ensuring that all neighborhoods receive equitable attention.

    1. Identifying Overburdened Areas  
    By tracking 311 issues, city officials and community organizations can pinpoint areas that experience a disproportionate share of reported problems. Some neighborhoods may face persistent infrastructure challenges or environmental concerns, and data analysis helps highlight where resources should be allocated to improve conditions.

    2. Holding Agencies Accountable  
    Analyzing 311 response data allows residents and policymakers to assess how effectively different departments and agencies address reported issues. By measuring response times and resolution rates, the city can identify bottlenecks, improve efficiency, and ensure that problems are being addressed in a timely manner.

    3. Detecting Chronic Issues & Repeat Offenders  
    Tracking reports over time enables the identification of recurring problems in specific locations. If certain areas repeatedly report the same issues—such as illegal dumping at the same site or persistent potholes on key roads—this suggests the need for long-term solutions rather than temporary fixes.

    4. Promoting Equitable City Services  
    A data-driven approach to 311 issues allows for an analysis of disparities in service delivery across different communities. If some neighborhoods experience significantly slower response times or lack adequate resolutions, city officials can investigate and work toward more equitable distribution of resources.

    5. Enhancing Public Engagement & Transparency  
    Providing residents with access to 311 data fosters civic engagement and trust in local government. When people see that their concerns are acknowledged and addressed, they are more likely to participate in local governance and advocate for improvements in their communities.

    6. Supporting Data-Driven Policy Decisions  
    City planners and policymakers can use 311 data to inform infrastructure investments, budget allocations, and strategic planning efforts. Data trends can help prioritize high-impact projects, ensuring that funds are spent where they are needed most.
    """,
    unsafe_allow_html=True
)

