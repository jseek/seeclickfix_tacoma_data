import streamlit as st
import pandas as pd

def display_aging_analysis(filtered_df):
    """Function to compute and display aging analysis."""
    st.subheader("Aging Analysis")
    st.markdown(
        "For issues that have not been closed, shows the median time to acknowledge an issue, "
        "the count of acknowledged issues, and the percentage of issues that have been acknowledged, "
        "grouped by the kind of issue."
    )

    # Filter relevant issues
    aging_df = filtered_df[filtered_df['status'].isin(["Open", "Acknowledged"])].copy()
    
    # Compute resolution and acknowledgment times
    aging_df['days_to_resolution'] = (aging_df['resolved_at'] - aging_df['created_at']).dt.days
    aging_df['days_to_acknowledge'] = (aging_df['acknowledged_at'] - aging_df['created_at']).dt.days
    aging_df['acknowledged'] = aging_df['acknowledged_at'].notna()

    # Group by issue summary
    aging_summary = aging_df.groupby('summary').agg(
        median_days_to_acknowledge=('days_to_acknowledge', 'median'),
        count_acknowledged=('acknowledged', 'sum'),
        issue_count=('summary', 'count')
    ).reset_index()

    # Compute percentage acknowledged
    aging_summary['percent_acknowledged'] = (aging_summary['count_acknowledged'] / aging_summary['issue_count']) * 100

    # Sort by issue count
    aging_summary = aging_summary.sort_values(by='issue_count', ascending=False)

    # Display results
    st.dataframe(aging_summary)
