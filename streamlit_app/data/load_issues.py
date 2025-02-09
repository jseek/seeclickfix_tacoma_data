import pandas as pd
import streamlit as st

@st.cache_data
def load_issues():
    """Loads the issues data from a Parquet file and preprocesses it."""
    df = pd.read_parquet("exports/seeclickfix_issues_dump.parquet")
    df['created_at'] = pd.to_datetime(df['created_at'])

    show_issues_after_date = '2024-01-01'
    df = df[df['created_at'] >= show_issues_after_date]

    df['updated_at'] = pd.to_datetime(df['updated_at'])
    df['acknowledged_at'] = pd.to_datetime(df['acknowledged_at'])
    df['closed_at'] = pd.to_datetime(df['closed_at'])

    df['homeless_related'] = df['summary'].str.contains("homeless|someone living on", case=False, na=False) | \
                            df['description'].str.contains("homeless", case=False, na=False)

    df['homeless_related'] = df['homeless_related'].map({True: 'homeless-related', False: 'other issues'})

    # Create formatted district display
    df['district_display'] = df['council_district'].fillna(0).astype(int).astype(str) + " - " + df['councilmember'].fillna("Unknown")
    
    # Create formatted police district-sector display
    df['police_district_sector'] = df['police_sector'].astype(str) + " - " + df['police_district'].astype(str)

    # Fill missing values for shelter-related fields
    df['within_10_blocks_of_shelter'] = df['within_10_blocks_of_shelter'].fillna(False)
    
    return df