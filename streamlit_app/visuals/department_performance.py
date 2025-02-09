import streamlit as st
import pandas as pd
from streamlit_app.visuals.maps.heatmap import render_heatmap

def prepare_department_data(df):
    # --- Compute time-based metrics ---
    df['time_to_acknowledge'] = (df['acknowledged_at'] - df['created_at']).dt.days
    df['time_to_close'] = (df['closed_at'] - df['created_at']).dt.days

    # --- Create department prefix from assignee_name ---
    # Split the assignee name by "_" and take the first part.
    df['assignee_department_prefix'] = df['assignee_name'].str.split("_").str[0]

    # --- Mapping dictionary: raw prefix to department ---
    department_mapping = {
        "NCS": "Neighborhood and Community Services",
        "TPD": "Tacoma Police Department",
        "Police Department - Traffic - JN": "Tacoma Police Department",
        "Police Department - Traffic - HM": "Tacoma Police Department",
        "ES": "Environmental Services",
        "PW": "Public Works",
        "311 Customer Support Center": "311 Support",
        "PDS Code Case": "Planning and Development Services",
        "T&L": "Public Works",
        "CMO": "City Manager’s Office",
        "PDS": "Planning and Development Services",
        "OEHR": "Office of Equity and Human Rights",
        "Public Works - D.S.": "Public Works",
        "Public Works - Streets - TD": "Public Works",
        "Public Works - Traffic - JK": "Public Works",
        "Public Works - Streets - NG": "Public Works",
        "Fire": "Tacoma Fire Department",
        "PPW Water Quality Specialist - Davidson": "Public Works",
        "PPW – Asst Airport Administrator - Propst": "Public Works",
        "PPW Water Quality Specialist - Thompson": "Public Works",
        "IT": "Information Technology",
        "TPU": "Tacoma Public Utilities",
        "TVE": "Tacoma Venues & Events",
        "CED": "Community & Economic Development"
    }

    # --- Map the raw department prefix to a new "department" column ---
    df['department'] = df['assignee_department_prefix'].map(department_mapping)
    
    return df

def filter_by_department(department_df):
    """
    Displays a dropdown for department filtering and returns a filtered DataFrame.
    """
    st.markdown("### Filter by department")
    # Get a sorted list of unique, non-null categories from the prepared data.
    categories = sorted(department_df['department'].dropna().unique())
    # Create a selectbox with a "Show All" option.
    selected_department = st.selectbox("Select Department", options=["Show All"] + categories)
    
    if selected_department != "Show All":
        st.write("Filtering by department:", selected_department)
        return department_df[department_df['department'] == selected_department]
    else:
        return department_df

def department_performance_stats(df):
    # --- Aggregate performance statistics by department ---
    department_stats = df.groupby('department').agg(
        total_issues=('id', 'count'),
        acknowledged_issues=('acknowledged_at', 'count'),
        closed_issues=('closed_at', 'count'),
        avg_time_to_acknowledge=('time_to_acknowledge', 'mean'),
        avg_time_to_close=('time_to_close', 'mean')
    ).reset_index()

    # Compute acknowledgment and closure rates.
    department_stats['acknowledgment_rate'] = (department_stats['acknowledged_issues'] / department_stats['total_issues']) * 100
    department_stats['closure_rate'] = (department_stats['closed_issues'] / department_stats['total_issues']) * 100

    # --- Determine the Top Issue Summary per department ---
    top_summary = (
        df.groupby(['department', 'summary'])
        .size()
        .reset_index(name='summary_count')
        .sort_values(['department', 'summary_count'], ascending=[True, False])
        .drop_duplicates(subset=['department'], keep='first')
        .rename(columns={'summary': 'top_issue_type'})
    )

    # Merge the top summary into the aggregated stats.
    department_stats = department_stats.merge(
        top_summary[['department', 'top_issue_type']], 
        on='department', 
        how='left'
    )

    # Sort the final results by total issues (descending).
    department_stats = department_stats.sort_values(by='total_issues', ascending=False)

    # --- Display the Results ---
    return st.dataframe(department_stats)

def display_department_performance(filtered_df):
    """Compute and display department performance statistics by mapped department department."""
    st.subheader("Department Performance Summary")
    
    # Prepare the data in a separate DataFrame.
    department_df = prepare_department_data(filtered_df)
    
    # Apply department filter using the separate helper function.
    df_filtered = filter_by_department(department_df)

    department_performance_stats(df_filtered)

