# filters/date_filter.py
import streamlit as st
from datetime import datetime, timedelta

def apply_date_filter(df):
    """
    Display quick date range options and return the selected date range.
    
    Quick options:
        - Current Week: Monday to today.
        - Current Month: 1st of the month to today.
        - Current Year: January 1st to today.
        - Past Two Calendar Years: Jan 1 of last year to today.
        - Custom: User selects a range via a slider.
    """
    # Get the overall date boundaries from the DataFrame
    dataset_min_date = df['created_at'].min().to_pydatetime()
    dataset_max_date = df['created_at'].max().to_pydatetime()
    
    # Use today's date as reference, but if the dataset doesn't extend to today, use dataset_max_date.
    today = datetime.today()
    if today > dataset_max_date:
        today = dataset_max_date

    # Quick options available for the date filter.
    quick_options = [
        "Current Week",
        "Current Month",
        "Current Year",
        "Past Two Calendar Years",
        "Custom"
    ]
    
    selected_option = st.radio("Quick Date Range Options", quick_options, index=quick_options.index("Custom"))
    
    if selected_option == "Current Week":
        # Compute Monday of the current week.
        start_date = today - timedelta(days=today.weekday())
        # Ensure the computed date is not before the dataset’s minimum.
        start_date = max(start_date, dataset_min_date)
        end_date = today
        
    elif selected_option == "Current Month":
        # First day of the current month.
        start_date = today.replace(day=1)
        start_date = max(start_date, dataset_min_date)
        end_date = today
        
    elif selected_option == "Current Year":
        # January 1st of the current year.
        start_date = today.replace(month=1, day=1)
        start_date = max(start_date, dataset_min_date)
        end_date = today
        
    elif selected_option == "Past Two Calendar Years":
        # For example, if today is in 2025, this sets the range from Jan 1, 2024 to today.
        start_date = today.replace(year=today.year - 1, month=1, day=1)
        start_date = max(start_date, dataset_min_date)
        end_date = today
        
    else:  # Custom
        start_date, end_date = st.slider(
            "Select Issue Created Date Range",
            min_value=dataset_min_date,
            max_value=dataset_max_date,
            value=(dataset_min_date, dataset_max_date)
        )
    
    st.write(f"Selected date range: {start_date.date()} to {end_date.date()}")
    return (start_date, end_date)