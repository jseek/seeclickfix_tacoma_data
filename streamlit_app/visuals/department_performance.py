import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px
import uuid
from streamlit_app.visuals.maps.heatmap import render_heatmap

def display_department_performance(filtered_df):
    """Compute and display department performance statistics by mapped department."""
    st.subheader("Department Performance Summary")
    
    # Prepare the data in a separate DataFrame.
    department_df = filtered_df
    
    # Apply department filter using the separate helper function.
    df_filtered = filter_by_department(department_df)

    department_performance_stats(df_filtered)
    
    st.divider()
    
    display_department_resolution_time(df_filtered)

def plot_issues_over_time(df):
    """Plots a time series of issue counts over time, grouped by department."""

    # Convert 'created_at' to datetime if not already
    df["created_at"] = pd.to_datetime(df["created_at"])

    # Aggregate issue count per department per day
    time_series = df.groupby([df["created_at"].dt.date, "department"]).size().reset_index(name="issue_count")

    # Create line chart
    fig = px.line(
        time_series,
        x="created_at",
        y="issue_count",
        color="department",
        title="Issues Over Time by Department",
        labels={"created_at": "Date", "issue_count": "Number of Issues", "department": "Department"},
    )

    # Display the chart
    st.plotly_chart(fig, use_container_width=True)

def plot_top_issue_per_department(df):
    """Creates a scatter plot of the top issue for each department with point size based on issue count."""

    # Group data to count issues per (department, summary)
    issue_counts = df.groupby(["department", "summary"]).size().reset_index(name="issue_count")

    # Find the top issue for each department (highest issue_count)
    top_issues_per_department = (
        issue_counts.sort_values(["department", "issue_count"], ascending=[True, False])
        .drop_duplicates(subset=["department"], keep="first")
    )

    # Filter original dataframe to only include the top issues per department
    df_filtered = df[df["summary"].isin(top_issues_per_department["summary"])]

    # Create scatter plot
    fig = px.scatter(
        top_issues_per_department, 
        x="department", 
        y="summary", 
        size="issue_count", 
        color="department",
        title="Top Issue for Each Department",
        labels={"summary": "Top Issue", "department": "Department", "issue_count": "Number of Issues"},
        hover_name="summary",
        size_max=50
    )

    # Display the plot
    st.plotly_chart(fig, use_container_width=True)

def filter_by_department(department_df):
    """
    Displays a dropdown for department filtering and returns a filtered DataFrame.
    """
    # Get a sorted list of unique, non-null departments from the prepared data.
    departments = sorted(department_df['department'].dropna().unique())
    # Create a selectbox with a "Show All" option.
    selected_department = st.selectbox("Select Department", options=["Show All"] + departments)
    
    if selected_department != "Show All":
        st.write("Filtering by department:", selected_department)
        return department_df[department_df['department'] == selected_department]
    else:
        return department_df

def department_performance_stats(df):
    # --- Aggregate performance statistics by department ---
    department_stats = df.groupby('department').agg(
        total_issues=('id', 'count'),
        acknowledged_issues=('acknowledged_at', 'count'),
        closed_issues=('closed_at', 'count'),
        avg_time_to_acknowledge=('time_to_acknowledge', 'mean'),
        avg_time_to_close=('time_to_close', 'mean')
    ).reset_index()

    # Compute acknowledgment and closure rates.
    department_stats['acknowledgment_rate'] = (department_stats['acknowledged_issues'] / department_stats['total_issues']) * 100
    department_stats['closure_rate'] = (department_stats['closed_issues'] / department_stats['total_issues']) * 100

    # --- Determine the Top Issue Summary per department ---
    top_summary = (
        df.groupby(['department', 'summary'])
        .size()
        .reset_index(name='summary_count')
        .sort_values(['department', 'summary_count'], ascending=[True, False])
        .drop_duplicates(subset=['department'], keep='first')
        .rename(columns={'summary': 'top_issue_type'})
    )

    # Merge the top summary into the aggregated stats.
    department_stats = department_stats.merge(
        top_summary[['department', 'top_issue_type']], 
        on='department', 
        how='left'
    )

    # Sort the final results by total issues (descending).
    department_stats = department_stats.sort_values(by='total_issues', ascending=False)

    # --- Display the Results ---
    return st.dataframe(department_stats)

def display_department_resolution_time(filtered_df):
    """Function to compute and display issue resolution time by department."""
    st.subheader("Issue Volume vs. Resolution Time by Department")

    # Compute median days to acknowledge or close
    filtered_df['median_days_to_resolve'] = (
        (filtered_df[['acknowledged_at', 'closed_at']].min(axis=1) - filtered_df['created_at']).dt.days
    )

    # Aggregate data by department
    department_agg = filtered_df.groupby('department').agg(
        issue_count=('id', 'count'),
        median_days_to_resolve=('median_days_to_resolve', 'median')
    ).reset_index()

    # User option to switch between logarithmic and linear scale
    axis_scale = st.radio("Select axis scale:", ('Linear', 'Logarithmic'), index=0)

    # Create scatter plot
    fig_scatter = px.scatter(
        department_agg, 
        x='median_days_to_resolve', 
        y='issue_count',
        text='department',
        labels={'median_days_to_resolve': 'Median Days to Acknowledge/Close', 'issue_count': 'Number of Issues'},
        title='Number of Issues vs. Median Days to Acknowledge/Close by Department'
    )

    fig_scatter.update_traces(textposition='top center')

    # Apply selected axis scale
    scale_type = 'log' if axis_scale == 'Logarithmic' else 'linear'
    fig_scatter.update_layout(
        xaxis_type=scale_type,
        yaxis_type=scale_type
    )

    # Display plot in Streamlit
    st.plotly_chart(fig_scatter)
