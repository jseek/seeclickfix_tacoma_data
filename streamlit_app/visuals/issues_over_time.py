import streamlit as st
import pandas as pd
import plotly.express as px

def display_issues_over_time(df):
    """Function to display the weekly time series of issues over time."""
    st.subheader("Issues Over Time (Weekly)")
    st.markdown("Number of issues created each week")

    # Convert created_at to week start date
    df['week'] = df['created_at'].dt.to_period('W').apply(lambda r: r.start_time)
    
    # Count issues per week
    time_series = df.groupby(df['week']).count()['id']

    # Display as a line chart
    st.line_chart(time_series)
