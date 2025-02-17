import streamlit as st
import pandas as pd
from datetime import timedelta
import plotly.express as px
from streamlit_app.visuals import issues_created_by_time_period

def heads_up(filtered_df):
    # Convert string dates to date objects
    filtered_df['created_at_date'] = pd.to_datetime(filtered_df['created_at'], errors='coerce').dt.date
    filtered_df['resolved_at_date'] = pd.to_datetime(filtered_df['resolved_at'], errors='coerce').dt.date

    # Determine the current date as the max date in the created_at_date column
    current_date = filtered_df['created_at_date'].max()
    
    # Define rolling 7-day periods:
    # Current period: from (current_date - 6 days) to current_date (inclusive)
    current_rolling_start = current_date - timedelta(days=6)
    # Previous period: from (current_date - 13 days) to (current_date - 7 days)
    previous_rolling_start = current_date - timedelta(days=13)
    previous_rolling_end = current_date - timedelta(days=7)

    # Filter the DataFrame for created and resolved issues in each rolling period
    created_at_current_df = filtered_df[
        (filtered_df['created_at_date'] >= current_rolling_start) & 
        (filtered_df['created_at_date'] <= current_date)
    ]
    resolved_at_current_df = filtered_df[
        (filtered_df['resolved_at_date'] >= current_rolling_start) & 
        (filtered_df['resolved_at_date'] <= current_date)
    ]
    created_at_previous_df = filtered_df[
        (filtered_df['created_at_date'] >= previous_rolling_start) & 
        (filtered_df['created_at_date'] <= previous_rolling_end)
    ]
    resolved_at_previous_df = filtered_df[
        (filtered_df['resolved_at_date'] >= previous_rolling_start) & 
        (filtered_df['resolved_at_date'] <= previous_rolling_end)
    ]
    
    value_column = 'summary'
    
    st.markdown("**Created (Last 7 Days vs Previous 7 Days)**")
    st.markdown(
        f"Comparing dates: **Last 7 Days:** {current_rolling_start} to {current_date} | **Previous 7 Days:** {previous_rolling_start} to {previous_rolling_end}"
    )
    created_card(
        created_at_current_df, 
        created_at_previous_df, 
        label_current="Issues Created (Last 7 Days)", 
        label_previous="Issues Created (Previous 7 Days)"
    )
    top_current_value = get_top_value(created_at_current_df, value_column)
    st.write(f"*Top Issue in Last 7 Days: {top_current_value} ({top_value_percent_of_whole(top_current_value, value_column, created_at_current_df)})*")
    
    st.write("---")
    
    st.markdown("**Resolved (Last 7 Days vs Previous 7 Days)**")
    st.markdown(
        f"Comparing dates: **Last 7 Days:** {current_rolling_start} to {current_date} | **Previous 7 Days:** {previous_rolling_start} to {previous_rolling_end}"
    )
    resolved_card(
        resolved_at_current_df, 
        resolved_at_previous_df, 
        label_current="Issues Resolved (Last 7 Days)", 
        label_previous="Issues Resolved (Previous 7 Days)"
    )
    top_resolved_value = get_top_value(resolved_at_current_df, value_column)
    st.write(f"*Top Issue Resolved in Last 7 Days: {top_resolved_value} ({top_value_percent_of_whole(top_resolved_value, value_column, resolved_at_current_df)})*")
    
    st.write("---")

    st.plotly_chart(plot_homeless_stacked_horizontal_bar_chart(created_at_current_df))

    st.write("---")

    st.plotly_chart(plot_summary_stacked_horizontal_bar_chart(created_at_current_df))


def created_card(this_df, previous_df, label_current="Current Period", label_previous="Previous Period"):
    col1, col2, col3 = st.columns(3)
    with col1:
        card_metric(this_df, label_current)
    with col2:
        card_metric(previous_df, label_previous)
    with col3:
        card_delta_percent(this_df, previous_df, "Created")

def resolved_card(this_df, previous_df, label_current="Current Period", label_previous="Previous Period"):
    col1, col2, col3 = st.columns(3)
    with col1:
        card_metric(this_df, label_current)
    with col2:
        card_metric(previous_df, label_previous)
    with col3:
        card_delta_percent(this_df, previous_df, "Resolved")

def card_metric(df, label):
    count = df.shape[0]
    st.metric(label=label, value=count)

def card_delta_percent(current_df, previous_df, action):
    current_count = current_df.shape[0]
    previous_count = previous_df.shape[0]
    if previous_count == 0:
        delta_str = "N/A"
    else:
        delta = ((current_count - previous_count) / previous_count) * 100
        delta_str = f"{delta:.2f}% {'↑' if delta > 0 else '↓'}"
    st.metric(label=f"Delta % ({action}: Current vs Previous)", value=delta_str)

def get_top_value(df: pd.DataFrame, column: str = "summary") -> str:
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in DataFrame.")
    return df[column].value_counts().idxmax()

def top_value_percent_of_whole(value, value_column, df):
    total_count = df[value_column].count()
    value_count = df[df[value_column] == value][value_column].count()
    return f"{value_count:,}, {(value_count / total_count) * 100:.2f}%"


def plot_homeless_stacked_horizontal_bar_chart(df, col='homeless_related'):
    """
    Creates a single horizontal stacked bar chart representing 100% of the data,
    partitioned by the percentage distribution of the values in the specified column.
    
    Parameters:
        df (pd.DataFrame): The DataFrame containing your data.
        col (str): The column to analyze. Default is 'homeless_related'.
        
    Returns:
        fig (plotly.graph_objects.Figure): A Plotly figure object.
        
    Usage:
        fig = plot_homeless_stacked_horizontal_bar_chart(your_dataframe)
        st.plotly_chart(fig)
    """
    # Count the values in the specified column.
    counts = df[col].value_counts()
    total = counts.sum()
    
    # Calculate percentages for each category.
    percentages = (counts / total * 100).round(2)
    
    # Create a DataFrame for plotting.
    # We'll use a dummy category so that all segments are in one stacked bar.
    data = pd.DataFrame({
        'Category': counts.index.astype(str),
        'Count': counts.values,
        'Percentage': percentages.values,
        'Dummy': 'All Records'
    })
    
    # Create the horizontal stacked bar chart.
    fig = px.bar(
        data,
        x='Percentage',
        y='Dummy',
        color='Category',
        orientation='h',
        text='Percentage',
        title='Homeless Related Distribution This Week'
    )
    
    # Update the trace to show percentage labels on each segment.
    fig.update_traces(texttemplate='%{text}%', textposition='inside')
    
    # Configure layout: stack bars and set the x-axis from 0 to 100.
    fig.update_layout(
        barmode='stack',
        xaxis_title='Percentage',
        yaxis_title='',
        xaxis_range=[0, 100],
        showlegend=True
    )
    
    return fig


def plot_summary_stacked_horizontal_bar_chart(df, col='summary'):
    """
    Creates a single horizontal stacked bar chart representing 100% of the data,
    partitioned by the percentage distribution of values in the specified summary column.
    
    Parameters:
        df (pd.DataFrame): The DataFrame containing your data.
        col (str): The column to analyze. Default is 'summary'.
        
    Returns:
        fig (plotly.graph_objects.Figure): A Plotly figure object with the stacked bar chart.
    
    Usage:
        fig = plot_summary_stacked_horizontal_bar_chart(your_dataframe)
        st.plotly_chart(fig)
    """
    # Count the unique values in the summary column.
    counts = df[col].value_counts()
    total = counts.sum()
    percentages = (counts / total * 100).round(2)
    
    # Build a DataFrame for plotting.
    # We use a dummy category ('All Records') so that all values are part of one bar.
    plot_data = pd.DataFrame({
        'Category': counts.index.astype(str),
        'Count': counts.values,
        'Percentage': percentages.values,
        'Dummy': 'All Records'
    })
    
    # Create a horizontal stacked bar chart.
    fig = px.bar(
        plot_data,
        x='Percentage',
        y='Dummy',
        color='Category',
        orientation='h',
        text='Percentage',
        title='Issue Distribution This Week'
    )
    
    # Update trace to display percentage text inside each segment.
    fig.update_traces(texttemplate='%{text}%', textposition='inside')
    
    # Update layout:
    # - Set bar mode to 'stack'
    # - Configure x-axis to range from 0 to 100 to represent 100%
    # - Ensure the legend is displayed
    fig.update_layout(
        barmode='stack',
        xaxis_title='Percentage',
        yaxis_title='',
        xaxis_range=[0, 100],
        showlegend=True
    )
    
    return fig
