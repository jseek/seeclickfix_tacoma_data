import streamlit as st
import plotly.express as px
import pandas as pd

def display_district_resolution_time(filtered_df):
    """Function to compute and display issue resolution time by council district."""
    st.subheader("Issue Volume vs. Resolution Time by District")

    # Compute median days to acknowledge or close
    filtered_df['median_days_to_resolve'] = (filtered_df[['acknowledged_at', 'closed_at']].min(axis=1) - filtered_df['created_at']).dt.days

    # Aggregate data by council district
    district_agg = filtered_df.groupby('district_display').agg(
        issue_count=('id', 'count'),
        median_days_to_resolve=('median_days_to_resolve', 'median')
    ).reset_index()

    # Create scatter plot
    fig_scatter = px.scatter(
        district_agg, 
        x='median_days_to_resolve', 
        y='issue_count',
        text='district_display',
        labels={'median_days_to_resolve': 'Median Days to Acknowledge/Close', 'issue_count': 'Number of Issues'},
        title='Number of Issues vs. Median Days to Acknowledge/Close by Council District'
    )

    fig_scatter.update_traces(textposition='top center')

    # Display plot in Streamlit
    st.plotly_chart(fig_scatter)
