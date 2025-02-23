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

    if selected_district != "All":
        df = df[df['district_display'] == selected_district]

    if selected_police_district_sectors:
        df = df[df['police_district_sector'].isin(selected_police_district_sectors)]

    if selected_equity_index != "All":
        df = df[df['equityindex'] == selected_equity_index]

    df = df[df['summary'].isin(selected_summaries)]

    if homeless_toggle:
        df = df[df['homeless_related'] == 'homeless-related']

    if shelter_toggle:
        df = df[df['within_10_blocks_of_shelter'] == True]

    non_date_df = df

    # Apply the filters to the DataFrame.
    df = df[(df['created_at'] >= date_range[0]) & (df['created_at'] <= date_range[1])]

    return df, non_date_df
