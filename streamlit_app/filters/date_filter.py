import streamlit as st

def apply_date_filter(df):
    """Display a date range slider and return the selected date range."""
    min_date = df['created_at'].min().to_pydatetime()
    max_date = df['created_at'].max().to_pydatetime()
    date_range = st.slider(
        "Select Issue Created Date Range",
        min_value=min_date,
        max_value=max_date,
        value=(min_date, max_date)
    )
    return date_range