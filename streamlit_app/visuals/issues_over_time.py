import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import uuid

def display_issues_over_time(df):
    # Get the selected time granularity from the radio buttons.
    selected_grandularity, human_readable_time_unit = select_time_granularity(default="Week")
    
    issues_created_by_time_period(df, selected_grandularity, human_readable_time_unit)

    
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
    selected_grandularity = st.radio("Select time granularity", options, index=default_index, horizontal=True)

    # Mapping from the human-readable unit to the pandas period code.
    period_codes = {"Day": "D", "Week": "W", "Month": "M", "Year": "Y"}
    period_code = period_codes[selected_grandularity]
    human_readable_time_unit = selected_grandularity

    return period_code, human_readable_time_unit

def issues_created_by_time_period(df, period_code, human_readable_time_unit):
    # Convert 'created_at' to the chosen time period.
    df['time_period'] = df['created_at'].dt.to_period(period_code).apply(lambda r: r.start_time)
    
    # Count the number of issues per period.
    time_series = df.groupby('time_period').count()['id']
    
    # Convert the Series into a DataFrame for Plotly.
    time_series_df = time_series.reset_index().rename(columns={'time_period': 'Date', 'id': 'Number of Issues'})
    
    # Create the line chart with markers.
    fig = px.line(
        time_series_df,
        x='Date',
        y='Number of Issues',
        title=f"Issues Created By {human_readable_time_unit}",
        labels={'Date': 'Date', 'Number of Issues': 'Number of Issues'},
        markers=True
    )
    
    # Create annotations for each point.
    annotations = []
    for _, row in time_series_df.iterrows():
        annotations.append(
            dict(
                x=row['Date'],
                y=row['Number of Issues'],
                text=str(row['Number of Issues']),
                textangle=270,  # Rotate text 90°.
                showarrow=False,
                xanchor='center',
                yanchor='bottom',
                yshift=10     # Offset the text.
            )
        )
    
    fig.update_layout(
        annotations=annotations,
        xaxis_title="Date",
        yaxis_title="Number of Issues"
    )
    
    # Generate a truly unique key using uuid4.
    unique_key = f"issues_chart_{period_code}_{human_readable_time_unit}_{uuid.uuid4()}"
    return st.plotly_chart(fig, key=unique_key)
