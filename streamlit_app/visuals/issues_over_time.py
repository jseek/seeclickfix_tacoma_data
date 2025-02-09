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
    Each point on the chart is labeled with the count of issues (rotated 90°) and offset from the point.
    """
    # Get the selected time granularity from the radio buttons.
    time_unit = select_time_granularity(default="Week")
    
    # Mapping from the human-readable unit to the pandas period code.
    period_codes = {"Day": "D", "Week": "W", "Month": "M", "Year": "Y"}
    period_code = period_codes[time_unit]
    
    # Convert 'created_at' to the chosen time period (using the start of that period).
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
        title=f"Issues Over Time ({time_unit})",
        labels={'Date': 'Date', 'Number of Issues': 'Number of Issues'},
        markers=True
    )
    
    # Create annotations for each point with rotated text (90°) and an offset (using yshift).
    annotations = []
    for _, row in time_series_df.iterrows():
        annotations.append(
            dict(
                x=row['Date'],
                y=row['Number of Issues'],
                text=str(row['Number of Issues']),
                textangle=270,       # Rotate the text 90 degrees.
                showarrow=False,
                xanchor='center',
                yanchor='bottom',
                yshift=10         # Offset the text 10 pixels above the marker.
            )
        )
    
    # Update layout to include the annotations and better axis titles.
    fig.update_layout(
        annotations=annotations,
        xaxis_title="Date",
        yaxis_title="Number of Issues"
    )
    
    # Display the chart in Streamlit.
    st.plotly_chart(fig)
