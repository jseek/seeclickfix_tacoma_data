import streamlit as st

def apply_equity_index_filter(df):
    # Define the custom order
    custom_order = {
        "Very High": 0,
        "High": 1,
        "Moderate": 2,
        "Low": 3,
        "Very Low": 4,
    }
    # Get unique options from the DataFrame and sort them using the custom order.
    unique_options = df['equityindex'].dropna().unique().tolist()
    options_sorted = sorted(unique_options, key=lambda x: custom_order.get(x, 99))
    
    # Prepend "All" so it appears as the first option.
    options = ["All"] + options_sorted

    with st.expander("Filter by Equity Index", expanded=False):
        selected = st.selectbox("Select Equity Index", options)
    return selected