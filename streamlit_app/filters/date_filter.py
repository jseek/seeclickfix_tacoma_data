import streamlit as st
from datetime import datetime, timedelta

def apply_date_filter(df):
    """
    Display quick date range options and return the selected date range.
    
    Quick options:
        - Current Week: Monday to today.
        - Current Month: 1st of the month to today.
        - Current Year: January 1st to today.
        - Past Two Calendar Years: January 1 of last year to today.
        - Previous 7 Days: From 7 days ago to today.
        - Previous 30 Days: From 30 days ago to today.
        - Rolling 1 Year: From 1 year ago to today.
        - Custom: User selects a range via a slider.
    """
    # Determine the dataset's date boundaries.
    dataset_min_date = df['created_at'].min().to_pydatetime()
    dataset_max_date = df['created_at'].max().to_pydatetime()
    
    # Use today’s date as a reference, but if the dataset’s max is earlier, use that.
    today = datetime.today()
    if today > dataset_max_date:
        today = dataset_max_date

    # Define quick option choices.
    quick_options = [
        "Current Week",
        "Current Month",
        "Current Year",
        "Past Two Calendar Years",
        "Previous 7 Days",
        "Previous 30 Days",
        "Rolling 1 Year",
        "Custom"
    ]
    
    # Default to "Past Two Calendar Years" (index 3)
    selected_option = st.radio("Select Date Range", quick_options, index=5)
    
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
        # For example, if today is in 2025, this sets the range from Jan 1, 2024 to today.
        start_date = today.replace(year=today.year - 1, month=1, day=1)
        start_date = max(start_date, dataset_min_date)
        end_date = today
        
    elif selected_option == "Previous 7 Days":
        start_date = today - timedelta(days=7)
        start_date = max(start_date, dataset_min_date)
        end_date = today
        
    elif selected_option == "Previous 30 Days":
        start_date = today - timedelta(days=30)
        start_date = max(start_date, dataset_min_date)
        end_date = today
        
    elif selected_option == "Rolling 1 Year":
        start_date = today - timedelta(days=365)
        start_date = max(start_date, dataset_min_date)
        end_date = today
        
    else:  # Custom
        # Only show the slider if "Custom" is selected.
        start_date, end_date = st.slider(
            "Select Issue Created Date Range",
            min_value=dataset_min_date,
            max_value=dataset_max_date,
            value=(dataset_min_date, dataset_max_date)
        )
    
    st.write(f"Selected date range: {start_date.date()} to {end_date.date()}")
    return (start_date, end_date)