import streamlit as st
import pandas as pd
import plotly.express as px

def select_time_granularity(default="Week"):
    """
    Renders horizontal radio buttons for time granularity selection.

    Parameters:
        default (str): The default selected time unit. Options: "Day", "Week", "Month", "Year".
    
    Returns:
        str: The selected time unit.
    """
    options = ["Day", "Week", "Month", "Year"]
    if default not in options:
        default = "Week"
    default_index = options.index(default)
    
    selected = st.radio("Select time granularity", options, index=default_index, horizontal=True)
    return selected

def display_issues_over_time(df):
    """
    Displays a time series line chart of issues with a user-selected granularity.
    The user can choose to view the data by Day, Week, Month, or Year using horizontal radio buttons.
    Each point on the chart is labeled with the count of issues.
    """
    # Use the separate function to get the selected time granularity
    time_unit = select_time_granularity(default="Week")
    
    # Mapping from the human-readable unit to the pandas period code
    period_codes = {"Day": "D", "Week": "W", "Month": "M", "Year": "Y"}
    period_code = period_codes[time_unit]
    
    # Convert 'created_at' to the chosen time period (using the start of that period)
    df['time_period'] = df['created_at'].dt.to_period(period_code).apply(lambda r: r.start_time)
    
    # Count the number of issues per period
    time_series = df.groupby('time_period').count()['id']
    
    # Convert the Series into a DataFrame for Plotly
    time_series_df = time_series.reset_index().rename(columns={'time_period': 'Date', 'id': 'Number of Issues'})
    
    # Create a line chart with markers and text labels for each data point.
    fig = px.line(
        time_series_df,
        x='Date',
        y='Number of Issues',
        title=f"Issues Over Time ({time_unit})",
        labels={'Date': 'Date', 'Number of Issues': 'Number of Issues'},
        markers=True,                # Show markers on the line
        text='Number of Issues'      # Use the count as text labels for each point
    )
    
    # Adjust the position of the text labels (e.g., above the markers)
    fig.update_traces(textposition='top center')
    
    # Update the layout for better axis titles
    fig.update_layout(xaxis_title="Date", yaxis_title="Number of Issues")
    
    # Display the chart in Streamlit
    st.plotly_chart(fig)
