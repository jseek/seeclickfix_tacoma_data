import streamlit as st

def apply_filters(df):
    """Function to display UI filters and return the filtered DataFrame."""
    col1, col2 = st.columns([1, 2])

    with col1:
        # Date range filter
        min_date, max_date = df['created_at'].min().to_pydatetime(), df['created_at'].max().to_pydatetime()
        date_range = st.slider("Select Issue Created Date Range", min_value=min_date, max_value=max_date, value=(min_date, max_date))

        # District filter
        district_options = ["All"] + sorted(df['district_display'].dropna().unique().tolist())
        selected_district = st.selectbox("Filter by City Council District", district_options)

        # Police district-sector filter
        police_district_sector_options = sorted(df['police_district_sector'].dropna().unique().tolist())
        with st.expander("Filter by Police Sector - District", expanded=False):
            selected_police_district_sectors = st.multiselect(
                "Select Police Sectors",
                police_district_sector_options,
                default=police_district_sector_options
            )

        # Equity Index filter
        equity_index_options = ["All"] + sorted(df['equityindex'].dropna().unique().tolist())
        selected_equity_index = st.selectbox("Filter by Equity Index", equity_index_options)

        # Issue Type filter
        st.markdown("Issue Type")
        summary_options = df['summary'].unique().tolist()
        with st.expander("Expand to select issue types"):
            selected_summaries = st.multiselect("Select Summaries", summary_options, default=summary_options)

        # Homeless-related filter
        homeless_toggle = st.toggle("Show only homeless-related issues", value=False)

        # Shelter Proximity filter
        shelter_toggle = st.toggle("Show only issues within 10 blocks of a shelter", value=False)

    # Apply filters to the DataFrame
    filtered_df = df[(df['created_at'] >= date_range[0]) & (df['created_at'] <= date_range[1])]

    if selected_district != "All":
        filtered_df = filtered_df[filtered_df['district_display'] == selected_district]

    if selected_police_district_sectors:
        filtered_df = filtered_df[filtered_df['police_district_sector'].isin(selected_police_district_sectors)]

    if selected_equity_index != "All":
        filtered_df = filtered_df[filtered_df['equityindex'] == selected_equity_index]

    if homeless_toggle:
        filtered_df = filtered_df[filtered_df['homeless_related'] == 'homeless-related']

    filtered_df = filtered_df[filtered_df['summary'].isin(selected_summaries)]

    # Apply shelter-related filters
    if shelter_toggle:
        filtered_df = filtered_df[filtered_df['within_10_blocks_of_shelter'] == True]

    return filtered_df, col2
