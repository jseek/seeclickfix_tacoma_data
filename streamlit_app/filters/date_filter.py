# filters/date_filter.py
import streamlit as st
from datetime import datetime, timedelta

def apply_date_filter(df):
    """
    Display quick date range options and return the selected date range.
    
    Available options:
      - Current Week: From Monday of the current week to today.
      - Current Month: From the 1st of the current month to today.
      - Current Year: From January 1 of the current year to today.
      - Past Two Calendar Years: From January 1 of last year to today.
    """
    # Determine the dataset's date boundaries.
    dataset_min_date = df['created_at'].min().to_pydatetime()
    dataset_max_date = df['created_at'].max().to_pydatetime()
    
    # Use today's date as reference; if today is after the dataset's max, use dataset_max_date.
    today = datetime.today()
    if today > dataset_max_date:
        today = dataset_max_date

    # Define quick option choices (no custom option).
    quick_options = [
        "Current Week",
        "Current Month",
        "Current Year",
        "Past Two Calendar Years"
    ]
    
    # Default to "Current Week"
    selected_option = st.radio("Select Date Range", quick_options, index=0)
    
    if selected_option == "Current Week":
        # Compute Monday of the current week.
        start_date = today - timedelta(days=today.weekday())
        start_date = max(start_date, dataset_min_date)
        end_date = today
        
    elif selected_option == "Current Month":
        # Use the 1st day of the current month.
        start_date = today.replace(day=1)
        start_date = max(start_date, dataset_min_date)
        end_date = today
        
    elif selected_option == "Current Year":
        # Use January 1 of the current year.
        start_date = today.replace(month=1, day=1)
        start_date = max(start_date, dataset_min_date)
        end_date = today
        
    elif selected_option == "Past Two Calendar Years":
        # Use January 1 of last year as the start date.
        start_date = today.replace(year=today.year - 1, month=1, day=1)
        start_date = max(start_date, dataset_min_date)
        end_date = today

    st.write(f"Selected date range: {start_date.date()} to {end_date.date()}")
    return (start_date, end_date)