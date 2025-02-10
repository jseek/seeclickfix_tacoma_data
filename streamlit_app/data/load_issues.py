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

    # First resolution either acknowledged or closed
    df['resolved_at'] = df[['acknowledged_at', 'closed_at']].min(axis=1)

    # --- Compute time-based metrics ---
    df['time_to_acknowledge'] = (df['acknowledged_at'] - df['created_at']).dt.days
    df['time_to_close'] = (df['closed_at'] - df['created_at']).dt.days

    df = prepare_department_data(df)

    return df

def prepare_department_data(df):
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