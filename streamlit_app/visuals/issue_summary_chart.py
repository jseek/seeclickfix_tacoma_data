import streamlit as st
import plotly.express as px

def display_issue_summary(filtered_df):
    """Function to display the horizontal bar chart for issue summary counts."""
    st.subheader("Issues by Type")
    st.markdown("Shows the most reported issues.")

    # Compute summary counts
    summary_counts = filtered_df['summary'].value_counts().sort_values(ascending=True)

    # Create horizontal bar chart
    fig_bar = px.bar(summary_counts, x=summary_counts.values, y=summary_counts.index, 
                     orientation='h', labels={'x': 'Count', 'y': 'Request Type'})

    # Display the chart
    st.plotly_chart(fig_bar)

    # Compute resolution time
    filtered_df['resolved_at'] = filtered_df[['acknowledged_at', 'closed_at']].min(axis=1)
    filtered_df['time_to_resolution'] = (filtered_df['resolved_at'] - filtered_df['created_at']).dt.days
