import streamlit as st
import pandas as pd

def display_assignee_performance(filtered_df):
    """Function to compute and display assignee performance statistics."""
    st.subheader("Assignee Performance Summary")

    # Compute time to acknowledge and close
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
    st.dataframe(assignee_stats)

    # Scatter plot (existing visualization)
    st.subheader("Issue Distribution by Assignee")
    st.scatter_chart(filtered_df[['longitude', 'latitude']])

    # Data table below the scatter plot
    st.subheader("Issues per Assignee")
    issue_counts = assignee_stats[['assignee_name', 'total_issues']].rename(columns={'total_issues': 'number_of_issues'})
    st.dataframe(issue_counts)