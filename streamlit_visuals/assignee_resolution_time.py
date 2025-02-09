import streamlit as st
import plotly.express as px
import pandas as pd

def display_assignee_resolution_time(filtered_df):
    """Function to compute and display issue resolution time by assignee."""
    st.subheader("Issue Resolution Time by Assignee")
    st.markdown(
        "Each point represents an assignee, showing the total number of issues assigned to them "
        "and the average time taken to acknowledge or close the issue."
    )

    # Compute assignee statistics
    assignee_stats = filtered_df.groupby('assignee_name').agg(
        num_issues=('id', 'count'),
        avg_time_to_resolution=('time_to_resolution', 'mean')
    ).reset_index()

    # Create scatter plot
    fig_scatter = px.scatter(
        assignee_stats, x='num_issues', y='avg_time_to_resolution',
        hover_data=['assignee_name'],
        labels={'num_issues': 'Number of Issues', 'avg_time_to_resolution': 'Avg Time to Resolution (days)'},
        title='Resolution Time vs. Number of Issues by Assignee'
    )

    # Display the chart
    st.plotly_chart(fig_scatter)
