import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

def heads_up(filtered_df):

    filtered_df['created_at_date'] = pd.to_datetime(filtered_df['created_at'], errors='coerce').dt.date
    filtered_df['created_at_date'] = pd.to_datetime(filtered_df['created_at'], errors='coerce').dt.date
    filtered_df['resolved_at_date'] = pd.to_datetime(filtered_df['resolved_at'], errors='coerce').dt.date

    current_date = filtered_df['created_at_date'].max()
    current_week_start = current_date - timedelta(days=current_date.weekday())
    days_into_current_week = current_date - current_week_start
    last_week_start = current_week_start - timedelta(days=7)
    last_week_to_date = current_week_start + days_into_current_week

    created_at_week_filtered_df = filtered_df[(filtered_df['created_at_date'] >= current_week_start)]
    resolved_at_week_filtered_df = filtered_df[(filtered_df['resolved_at_date'] >= current_week_start)]

    created_at_last_week_filtered_df = filtered_df[(filtered_df['created_at_date'] >= last_week_start & filtered_df['created_at_date'] <= last_week_to_date)]
    resolved_at_last_week_filtered_df = filtered_df[(filtered_df['resolved_at_date'] >= last_week_start & filtered_df['resolved_at_date'] <= last_week_to_date)]

    dates_card(current_date, current_week_start, last_week_start, last_week_to_date)

    # created_card(created_at_week_filtered_df, resolved_at_week_filtered_df, created_at_last_week_filtered_df, resolved_at_last_week_filtered_df)

    # st.write("---")  # Optional separator
    
    # resolved_card(filtered_df, current_date, current_week_start, last_week_start, last_week_to_date)

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


def created_card(created_at_week_filtered_df, resolved_at_week_filtered_df, created_at_last_week_filtered_df, resolved_at_last_week_filtered_df):
    created_col1, created_col2, created_col3 = st.columns(3)
    with created_col1:
            card_issues_created_this_week(created_at_week_filtered_df)
    with created_col2:
            card_issues_created_last_week(created_at_last_week_filtered_df)
    with created_col3:
            card_delta_percent_created(created_at_week_filtered_df, created_at_last_week_filtered_df)


def resolved_card(filtered_df, current_date, current_week_start, last_week_start, last_week_to_date):
    resolved_col1, resolved_col2, resolved_col3 = st.columns(3)
    with resolved_col1:
            card_issues_resolved_this_week(filtered_df, current_date, current_week_start, last_week_start, last_week_to_date)
    with resolved_col2:
            card_issues_resolved_last_week(filtered_df, current_date, current_week_start, last_week_start, last_week_to_date)
    with resolved_col3:
            card_delta_percent_resolved(filtered_df, current_date, current_week_start, last_week_start, last_week_to_date)


def card_issues_created_this_week(created_at_week_filtered_df):
    """
    Displays a metric card with the count of issues created this week
    (from Monday up to the provided current_week_start).
    """
    
    # Filter issues created from week_start up to current_week_start
    count = created_at_week_filtered_df.shape[0]
    
    return st.metric(label="Issues Created This Week", value=count)


def card_issues_created_last_week(created_at_last_week_filtered_df):
    """
    Displays a metric card with the count of issues created last week
    (from last week’s Monday up to the same day-of-week as current_week_start).
    """
    count = created_at_last_week_filtered_df.shape[0]
    
    return st.metric(label="Issues Created Last Week", value=count)


def card_delta_percent_created(created_at_week_filtered_df, created_at_last_week_filtered_df):
    current_week_count = created_at_week_filtered_df.shape[0]
    last_week_count = created_at_last_week_filtered_df.shape[0]
    
    if last_week_count == 0:
        delta_str = "N/A"
    else:
        delta = ((current_week_count - last_week_count) / last_week_count) * 100
        delta_str = f"{delta:.2f}%"
    
    return st.metric(label="Delta % (Created: This Week vs Last Week)", value=delta_str)


# def card_issues_resolved_this_week(
#         filtered_df: pd.DataFrame
#         , current_date: datetime
#         , current_week_start: datetime
#         , last_week_start: datetime
#         , last_week_to_date: datetime
#     ):
#     """
#     Displays a metric card with the count of issues resolved this week
#     (from Monday up to the provided current_week_start).
#     """
#     current_week_start = pd.to_datetime(current_week_start)
#     week_start = current_week_start - timedelta(days=current_week_start.weekday())
    
#     # Convert 'resolved_at_date' to datetime (ignoring errors if blank/NaT)
#     filtered_df['resolved_at_date'] = pd.to_datetime(filtered_df['resolved_at_date'], errors='coerce')
    
#     current_week_resolved = filtered_df[(filtered_df['resolved_at_date'] >= week_start) & (filtered_df['resolved_at_date'] <= current_week_start)]
#     count = current_week_resolved.shape[0]
    
#     return st.metric(label="Issues Resolved This Week", value=count)


# def card_issues_resolved_last_week(
#         filtered_df: pd.DataFrame
#         , current_date: datetime
#         , current_week_start: datetime
#         , last_week_start: datetime
#         , last_week_to_date: datetime
#     ):
#     """
#     Displays a metric card with the count of issues resolved last week
#     (from last week’s Monday up to the same day-of-week as current_week_start).
#     """
#     current_week_start = pd.to_datetime(current_week_start)
#     current_week_start = current_week_start - timedelta(days=current_week_start.weekday())
#     last_week_start = current_week_start - timedelta(days=7)
#     last_week_end = last_week_start + timedelta(days=current_week_start.weekday())
    
#     filtered_df['resolved_at_date'] = pd.to_datetime(filtered_df['resolved_at_date'], errors='coerce')
    
#     last_week_resolved = filtered_df[(filtered_df['resolved_at_date'] >= last_week_start) & (filtered_df['resolved_at_date'] <= last_week_end)]
#     count = last_week_resolved.shape[0]
    
#     return st.metric(label="Issues Resolved Last Week", value=count)


# def card_delta_percent_resolved(
#         filtered_df: pd.DataFrame
#         , current_date: datetime
#         , current_week_start: datetime
#         , last_week_start: datetime
#         , last_week_to_date: datetime
#     ):
#     """
#     Displays a metric card showing the percent change (delta) in the number of issues
#     resolved this week compared to last week (up to the current day-of-week).
#     """
#     current_week_start = pd.to_datetime(current_week_start)
#     current_week_start = current_week_start - timedelta(days=current_week_start.weekday())
#     last_week_start = current_week_start - timedelta(days=7)
#     last_week_end = last_week_start + timedelta(days=current_week_start.weekday())
    
#     filtered_df['resolved_at_date'] = pd.to_datetime(filtered_df['resolved_at_date'], errors='coerce')
    
#     current_week_count = filtered_df[(filtered_df['resolved_at_date'] >= current_week_start) & (filtered_df['resolved_at_date'] <= current_week_start)].shape[0]
#     last_week_count = filtered_df[(filtered_df['resolved_at_date'] >= last_week_start) & (filtered_df['resolved_at_date'] <= last_week_end)].shape[0]
    
#     if last_week_count == 0:
#         delta_str = "N/A"
#     else:
#         delta = ((current_week_count - last_week_count) / last_week_count) * 100
#         delta_str = f"{delta:.2f}%"
    
#     return st.metric(label="Delta % (Resolved: This Week vs Last Week)", value=delta_str)
