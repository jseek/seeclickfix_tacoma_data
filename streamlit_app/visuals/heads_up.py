import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
from streamlit_app.visuals import (
    issues_created_by_time_period,
)


def heads_up(filtered_df):

    filtered_df['created_at_date'] = pd.to_datetime(filtered_df['created_at'], errors='coerce').dt.date
    filtered_df['created_at_date'] = pd.to_datetime(filtered_df['created_at'], errors='coerce').dt.date
    filtered_df['resolved_at_date'] = pd.to_datetime(filtered_df['resolved_at'], errors='coerce').dt.date

    current_date = filtered_df['created_at_date'].max()
    current_week_start = current_date - timedelta(days=current_date.weekday())
    days_into_current_week = current_date - current_week_start
    last_week_start = current_week_start - timedelta(days=7)
    last_week_to_date = current_date - timedelta(days=7)

    created_at_week_filtered_df = filtered_df[(filtered_df['created_at_date'] >= current_week_start)]
    resolved_at_week_filtered_df = filtered_df[(filtered_df['resolved_at_date'] >= current_week_start)]
    created_at_last_week_filtered_df = filtered_df[(filtered_df['created_at_date'] >= last_week_start) & (filtered_df['created_at_date'] <= last_week_to_date)]
    resolved_at_last_week_filtered_df = filtered_df[(filtered_df['resolved_at_date'] >= last_week_start) & (filtered_df['resolved_at_date'] <= last_week_to_date)]

    # dates_card(current_date, current_week_start, last_week_start, last_week_to_date)

    value_column = 'summary'

    st.markdown("**Created Last Week**")
    created_card(created_at_week_filtered_df, created_at_last_week_filtered_df)
    top_this_week_value = get_top_value(created_at_week_filtered_df, value_column)
    st.write(f"*Top Issue This Week: {top_this_week_value} ({top_value_percent_of_whole(top_this_week_value, value_column, created_at_week_filtered_df)})*")
    st.write("---")
    st.markdown("**Resolved Last Week**")
    resolved_card(resolved_at_week_filtered_df, resolved_at_last_week_filtered_df)
    top_last_week_value = get_top_value(resolved_at_week_filtered_df, value_column)
    st.write(f"*Top Issue Last Week: {top_last_week_value} ({top_value_percent_of_whole(top_last_week_value, value_column, resolved_at_week_filtered_df)})*")
    
    st.write("---")

    issues_created_by_time_period(filtered_df, "W", "Week")

    st.write("---")

    st.plotly_chart(plot_homeless_stacked_horizontal_bar_chart(created_at_week_filtered_df))

    st.write("---")

    st.plotly_chart(plot_summary_stacked_horizontal_bar_chart(created_at_week_filtered_df))


def dates_card(current_date, current_week_start, last_week_start, last_week_to_date):
    dates_col1, dates_col2, dates_col3, dates_col4 = st.columns(4)
    with dates_col1:
        st.markdown("<p style='text-align: center;'>Max Data Date</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center;'>{current_date}</p>", unsafe_allow_html=True)
    with dates_col2:
        st.markdown("<p style='text-align: center;'>Week Start Date</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center;'>{current_week_start}</p>", unsafe_allow_html=True)
    with dates_col3:
        st.markdown("<p style='text-align: center;'>Last Week Start Date</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center;'>{last_week_start}</p>", unsafe_allow_html=True)
    with dates_col4:
        st.markdown("<p style='text-align: center;'>Last Week To Date</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center;'>{last_week_to_date}</p>", unsafe_allow_html=True)


def created_card(this_week_df, last_week_df):
    created_col1, created_col2, created_col3 = st.columns(3)
    with created_col1:
            card_issues_created_this_week(this_week_df)
    with created_col2:
            card_issues_created_last_week(last_week_df)
    with created_col3:
            card_delta_percent_created(this_week_df, last_week_df)


def resolved_card(this_week_df, last_week_df):
    resolved_col1, resolved_col2, resolved_col3 = st.columns(3)
    with resolved_col1:
            card_issues_resolved_this_week(this_week_df)
    with resolved_col2:
            card_issues_resolved_last_week(last_week_df)
    with resolved_col3:
            card_delta_percent_resolved(this_week_df, last_week_df)


def card_issues_created_this_week(this_week_df):
    """
    Displays a metric card with the count of issues created this week
    (from Monday up to the provided current_week_start).
    """
    
    # Filter issues created from week_start up to current_week_start
    count = this_week_df.shape[0]
    
    st.metric(label="Issues Created This Week", value=count)


def card_issues_created_last_week(last_week_df):
    """
    Displays a metric card with the count of issues created last week
    (from last week’s Monday up to the same day-of-week as current_week_start).
    """
    count = last_week_df.shape[0]


    st.metric(label="Issues Created Last Week", value=count)
    st.caption("Calculated as: Issues Created Last Week (To Current Weekday, for comparison of WTD)")


def card_delta_percent_created(this_week_df, last_week_df):
    current_week_count = this_week_df.shape[0]
    last_week_count = last_week_df.shape[0]
    
    if last_week_count == 0:
        delta_str = "N/A"
    else:
        delta = ((current_week_count - last_week_count) / last_week_count) * 100
        if delta > 0:
            delta_str = f"{delta:.2f}% ↑"
        else:
            delta_str = f"{delta:.2f}% ↓"
    
    st.metric(label="Delta % (Created: This Week vs Last Week)", value=delta_str)


def card_issues_resolved_this_week(this_week_df):
    """
    Displays a metric card with the count of issues created this week
    (from Monday up to the provided current_week_start).
    """
    
    # Filter issues created from week_start up to current_week_start
    count = this_week_df.shape[0]
    
    st.metric(label="Issues Resolved This Week", value=count)


def card_issues_resolved_last_week(last_week_df):
    """
    Displays a metric card with the count of issues created last week
    (from last week’s Monday up to the same day-of-week as current_week_start).
    """
    count = last_week_df.shape[0]
    
    st.metric(label="Issues Resolved Last Week", value=count)
    st.caption("Calculated as: Issues Resolved Last Week (To Current Weekday, for comparison of WTD)")


def card_delta_percent_resolved(this_week_df, last_week_df):
    current_week_count = this_week_df.shape[0]
    last_week_count = last_week_df.shape[0]
    
    if last_week_count == 0:
        delta_str = "N/A"
    else:
        delta = ((current_week_count - last_week_count) / last_week_count) * 100
        if delta > 0:
            delta_str = f"{delta:.2f}% ↑"
        else:
            delta_str = f"{delta:.2f}% ↓"
    
    st.metric(label="Delta % (Resolved: This Week vs Last Week)", value=delta_str)


def get_top_value(df: pd.DataFrame, column: str = "summary") -> str:
    """
    Returns the most frequently occurring value in the specified column of a DataFrame.

    :param df: The input DataFrame.
    :param column: The column name to analyze (default is "summary").
    :return: The most frequent summary value.
    """
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in DataFrame.")

    top_value = df[column].value_counts().idxmax()
    return top_value

def top_value_percent_of_whole(value, value_column, df):
    """
    Returns the percentage of the total count that the specified value represents.

    :param value: The value to calculate the percentage for.
    :param value_column: The column name to analyze.
    :param df: The input DataFrame.
    :return: The percentage of the total count that the specified value represents.
    """
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
