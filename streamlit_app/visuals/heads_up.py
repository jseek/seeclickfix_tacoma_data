import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

def heads_up(df, filtered_df):

    df['created_at_date'] = pd.to_datetime(df['created_at'], errors='coerce').dt.date
    filtered_df['created_at_date'] = pd.to_datetime(filtered_df['created_at'], errors='coerce').dt.date
    filtered_df['resolved_at_date'] = pd.to_datetime(filtered_df['resolved_at'], errors='coerce').dt.date
    current_date = df['created_at_date'].max()
    week_start = current_date - timedelta(days=current_date.weekday())


    st.write("Max Data Date:", current_date)
    st.write("Week Start Date:", week_start)

    created_col1, created_col2, created_col3 = st.columns(3)
    with created_col1:
            card_issues_created_this_week(filtered_df, current_date)
    with created_col2:
            card_issues_created_last_week(filtered_df, current_date)
    with created_col3:
            card_delta_percent_created(filtered_df, current_date)

    st.write("---")  # Optional separator
    
    resolved_col1, resolved_col2, resolved_col3 = st.columns(3)
    with resolved_col1:
            card_issues_resolved_this_week(filtered_df, current_date)
    with resolved_col2:
            card_issues_resolved_last_week(filtered_df, current_date)
    with resolved_col3:
            card_delta_percent_resolved(filtered_df, current_date)


def card_issues_created_this_week(df: pd.DataFrame, current_date: datetime):
    """
    Displays a metric card with the count of issues created this week
    (from Monday up to the provided current_date).
    """
    # Ensure current_date is a Timestamp
    current_date = pd.to_datetime(current_date)
    # Find Monday of the current week
    week_start = current_date - timedelta(days=current_date.weekday())
    
    # Convert 'created_at_date' column to datetime if not already
    df['created_at_date'] = pd.to_datetime(df['created_at_date'], errors='coerce')
    
    # Filter issues created from week_start up to current_date
    current_week_issues = df[(df['created_at_date'] >= week_start) & (df['created_at_date'] <= current_date)]
    count = current_week_issues.shape[0]
    
    return st.metric(label="Issues Created This Week", value=count)


def card_issues_created_last_week(df: pd.DataFrame, current_date: datetime):
    """
    Displays a metric card with the count of issues created last week
    (from last week’s Monday up to the same day-of-week as current_date).
    """
    current_date = pd.to_datetime(current_date)
    # Monday of the current week
    current_week_start = current_date - timedelta(days=current_date.weekday())
    # Monday of last week
    last_week_start = current_week_start - timedelta(days=7)
    # Last week's "current day" is offset by the same weekday number as current_date
    last_week_end = last_week_start + timedelta(days=current_date.weekday())
    
    df['created_at_date'] = pd.to_datetime(df['created_at_date'], errors='coerce')
    
    last_week_issues = df[(df['created_at_date'] >= last_week_start) & (df['created_at_date'] <= last_week_end)]
    count = last_week_issues.shape[0]
    
    return st.metric(label="Issues Created Last Week", value=count)


def card_delta_percent_created(df: pd.DataFrame, current_date: datetime):
    """
    Displays a metric card showing the percent change (delta) in the number of issues
    created in the full week (Monday through Sunday) of the current week compared to
    last week.
    """
    # Convert current_date to a date (dropping any time component)
    current_date = pd.to_datetime(current_date).date()
    
    # Determine the Monday of the current week
    current_week_start = current_date - timedelta(days=current_date.weekday())
    # Use the full week: Monday to Sunday
    current_week_end = current_week_start + timedelta(days=6)
    
    # For last week, use the same full week range
    last_week_start = current_week_start - timedelta(days=7)
    last_week_end = last_week_start + timedelta(days=6)
    
    # Convert the DataFrame column to date
    df['created_at_date'] = pd.to_datetime(df['created_at_date'], errors='coerce').dt.date
    
    current_week_count = df[
        (df['created_at_date'] >= current_week_start) &
        (df['created_at_date'] <= current_week_end)
    ].shape[0]
    
    last_week_count = df[
        (df['created_at_date'] >= last_week_start) &
        (df['created_at_date'] <= last_week_end)
    ].shape[0]
    
    if last_week_count == 0:
        delta_str = "N/A"
    else:
        delta = ((current_week_count - last_week_count) / last_week_count) * 100
        delta_str = f"{delta:.2f}%"
    
    return st.metric(label="Delta % (Created: This Week vs Last Week)", value=delta_str)


def card_issues_resolved_this_week(df: pd.DataFrame, current_date: datetime):
    """
    Displays a metric card with the count of issues resolved this week
    (from Monday up to the provided current_date).
    """
    current_date = pd.to_datetime(current_date)
    week_start = current_date - timedelta(days=current_date.weekday())
    
    # Convert 'resolved_at_date' to datetime (ignoring errors if blank/NaT)
    df['resolved_at_date'] = pd.to_datetime(df['resolved_at_date'], errors='coerce')
    
    current_week_resolved = df[(df['resolved_at_date'] >= week_start) & (df['resolved_at_date'] <= current_date)]
    count = current_week_resolved.shape[0]
    
    return st.metric(label="Issues Resolved This Week", value=count)


def card_issues_resolved_last_week(df: pd.DataFrame, current_date: datetime):
    """
    Displays a metric card with the count of issues resolved last week
    (from last week’s Monday up to the same day-of-week as current_date).
    """
    current_date = pd.to_datetime(current_date)
    current_week_start = current_date - timedelta(days=current_date.weekday())
    last_week_start = current_week_start - timedelta(days=7)
    last_week_end = last_week_start + timedelta(days=current_date.weekday())
    
    df['resolved_at_date'] = pd.to_datetime(df['resolved_at_date'], errors='coerce')
    
    last_week_resolved = df[(df['resolved_at_date'] >= last_week_start) & (df['resolved_at_date'] <= last_week_end)]
    count = last_week_resolved.shape[0]
    
    return st.metric(label="Issues Resolved Last Week", value=count)


def card_delta_percent_resolved(df: pd.DataFrame, current_date: datetime):
    """
    Displays a metric card showing the percent change (delta) in the number of issues
    resolved this week compared to last week (up to the current day-of-week).
    """
    current_date = pd.to_datetime(current_date)
    current_week_start = current_date - timedelta(days=current_date.weekday())
    last_week_start = current_week_start - timedelta(days=7)
    last_week_end = last_week_start + timedelta(days=current_date.weekday())
    
    df['resolved_at_date'] = pd.to_datetime(df['resolved_at_date'], errors='coerce')
    
    current_week_count = df[(df['resolved_at_date'] >= current_week_start) & (df['resolved_at_date'] <= current_date)].shape[0]
    last_week_count = df[(df['resolved_at_date'] >= last_week_start) & (df['resolved_at_date'] <= last_week_end)].shape[0]
    
    if last_week_count == 0:
        delta_str = "N/A"
    else:
        delta = ((current_week_count - last_week_count) / last_week_count) * 100
        delta_str = f"{delta:.2f}%"
    
    return st.metric(label="Delta % (Resolved: This Week vs Last Week)", value=delta_str)
