# filters/filters.py
import streamlit as st
from .date_filter import apply_date_filter
from .district_filter import apply_district_filter
from .police_district_filter import apply_police_district_filter
from .equity_index_filter import apply_equity_index_filter
from .issue_type_filter import apply_issue_type_filter
from .homeless_filter import apply_homeless_filter
from .shelter_proximity_filter import apply_shelter_proximity_filter

def apply_filters(df):
    """Display UI filters and return the filtered DataFrame."""
    
    # Apply individual filters.
    date_range = apply_date_filter(df)
    selected_district = apply_district_filter(df)
    selected_police_district_sectors = apply_police_district_filter(df)
    selected_equity_index = apply_equity_index_filter(df)
    selected_summaries = apply_issue_type_filter(df)
    homeless_toggle = apply_homeless_filter()
    shelter_toggle = apply_shelter_proximity_filter()

    # Apply the filters to the DataFrame.
    filtered_df = df[(df['created_at'] >= date_range[0]) & (df['created_at'] <= date_range[1])]

    if selected_district != "All":
        filtered_df = filtered_df[filtered_df['district_display'] == selected_district]

    if selected_police_district_sectors:
        filtered_df = filtered_df[filtered_df['police_district_sector'].isin(selected_police_district_sectors)]

    if selected_equity_index != "All":
        filtered_df = filtered_df[filtered_df['equityindex'] == selected_equity_index]

    filtered_df = filtered_df[filtered_df['summary'].isin(selected_summaries)]

    if homeless_toggle:
        filtered_df = filtered_df[filtered_df['homeless_related'] == 'homeless-related']

    if shelter_toggle:
        filtered_df = filtered_df[filtered_df['within_10_blocks_of_shelter'] == True]

    return filtered_df
