import streamlit as st
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import json
import re
import hashlib

@st.cache_data
def load_geojson():
    with open("exports/City_Council_Districts.geojson", "r", encoding="utf-8") as f:
        return json.load(f)


def council_districts(filtered_df):
    
    councilmember_scatterplot(filtered_df)

    top_summary_by_district(filtered_df)

def councilmember_scatterplot(df):
    """Function to compute and display issue resolution time by council district."""
    st.subheader("Issue Volume vs. Resolution Time by District")

    # Aggregate data by council district
    district_agg = df.groupby('district_display').agg(
        issue_count=('id', 'count'),
        median_days_to_resolve=('days_to_resolve', 'median')
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
    return st.plotly_chart(fig_scatter)

def top_summary_by_district(df):
    st.subheader("Top Issue Type by Council District")

    # Ensure the necessary columns exist
    if not {'summary', 'district_display'}.issubset(df.columns):
        st.error("DataFrame must contain 'summary' and 'district_display' columns")
        return None
    
    # Group by council district and find the most common summary
    top_summaries = (
        df.groupby(['district_display', 'summary'])
        .size()
        .reset_index(name='count')
        .sort_values(['district_display', 'count'], ascending=[True, False])
        .drop_duplicates(subset=['district_display'], keep='first')
    )

    # Rename 'summary' to 'issue'
    top_summaries = top_summaries.rename(columns={'summary': 'issue'})
    top_summaries = top_summaries.rename(columns={'district_display': 'district'})

    return st.dataframe(top_summaries[['district', 'issue', 'count']])
