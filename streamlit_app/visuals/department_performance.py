import streamlit as st
import pandas as pd
import pydeck as pdk
from streamlit_app.visuals.maps.heatmap import render_heatmap  # Retain your other imports as needed

def display_department_performance(filtered_df):
    """Compute and display department performance statistics by mapped department."""
    st.subheader("Department Performance Summary")
    
    # Prepare the data in a separate DataFrame.
    department_df = prepare_department_data(filtered_df)
    
    # Apply department filter using the separate helper function.
    df_filtered = filter_by_department(department_df)

    department_performance_stats(df_filtered)
    st.divider()
    display_issue_map(df_filtered)

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
    # Get a sorted list of unique, non-null departments from the prepared data.
    departments = sorted(department_df['department'].dropna().unique())
    # Create a selectbox with a "Show All" option.
    selected_department = st.selectbox("Select Department", options=["Show All"] + departments)
    
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

import streamlit as st
import pydeck as pdk
import pandas as pd

def display_map_legend(department_color_mapping):
    """
    Creates an HTML legend from the department_color_mapping dictionary and displays it.
    """
    legend_html = """
    <div style='position: relative; z-index: 1000; background: white; padding: 10px; border: 1px solid #ccc; margin-top: 10px;'>
      <b>Legend</b><br>
    """
    for department, color in department_color_mapping.items():
        color_str = f"rgb({color[0]},{color[1]},{color[2]})"
        legend_html += f"""
        <div style='display: flex; align-items: center; margin-bottom: 4px;'>
          <span style='background:{color_str}; width: 12px; height: 12px; display: inline-block; margin-right: 8px;'></span>
          {department}
        </div>
        """
    legend_html += "</div>"
    st.markdown(legend_html, unsafe_allow_html=True)

import streamlit as st
import pydeck as pdk
import pandas as pd
import streamlit.components.v1 as components
#from streamlit_app.visuals.maps.heatmap import render_heatmap  # Retain if needed

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

def display_map_legend(department_color_mapping):
    """
    Creates an HTML legend from the department_color_mapping dictionary and renders it using st.components.v1.html.
    """
    legend_html = """
    <div style="position: relative; z-index: 1000; background: white; padding: 10px; border: 1px solid #ccc; margin-top: 10px;">
      <b>Legend</b><br>
    """
    for department, color in department_color_mapping.items():
        color_str = f"rgb({color[0]},{color[1]},{color[2]})"
        legend_html += f"""
        <div style="display: flex; align-items: center; margin-bottom: 4px;">
          <span style="background: {color_str}; width: 12px; height: 12px; display: inline-block; margin-right: 8px;"></span>
          {department}
        </div>
        """
    legend_html += "</div>"
    # Use st.components.v1.html to render the HTML legend.
    components.html(legend_html, height=200)

def display_issue_map(df):
    """
    Prepares and displays a map of issues as points on a map.
    Each point is colored based on its department.
    
    Expects the DataFrame to contain:
      - 'lat': Latitude (float)
      - 'lng': Longitude (float)
      - 'assignee_name': Used to determine the department.
    
    The function uses the prepare_department_data() function to ensure the department column exists.
    """
    # Prepare the data (adds department, time metrics, etc.)
    df = prepare_department_data(df.copy())
    
    # Check if 'lat' and 'lng' columns exist.
    if 'lat' not in df.columns or 'lng' not in df.columns:
        st.error("The DataFrame must contain 'lat' and 'lng' columns.")
        return
    
    # Define a color mapping for departments (RGB format).
    department_color_mapping = {
        "Neighborhood and Community Services": [255, 0, 0],
        "Tacoma Police Department": [0, 255, 0],
        "Environmental Services": [0, 0, 255],
        "Public Works": [255, 255, 0],
        "311 Support": [255, 0, 255],
        "Planning and Development Services": [0, 255, 255],
        "City Manager’s Office": [128, 0, 128],
        "Office of Equity and Human Rights": [128, 128, 0],
        "Tacoma Fire Department": [0, 128, 128],
        "Information Technology": [128, 128, 128],
        "Tacoma Public Utilities": [255, 165, 0],
        "Tacoma Venues & Events": [255, 20, 147],
        "Community & Economic Development": [0, 0, 0]
    }
    
    # Assign a color to each row based on its department.
    df["color"] = df["department"].apply(lambda d: department_color_mapping.get(d, [200, 200, 200]))
    
    # Create a PyDeck ScatterplotLayer.
    scatter_layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position='[lng, lat]',
        get_color="color",
        get_radius=50,  # Adjust the radius as needed (in meters)
        pickable=True,
        auto_highlight=True,
    )
    
    # Create an initial view state centered on the mean location.
    view_state = pdk.ViewState(
        latitude=df["lat"].mean(),
        longitude=df["lng"].mean(),
        zoom=11,
        pitch=0,
    )
    
    # Create a Deck instance with a tooltip showing department and issue id.
    deck = pdk.Deck(
        layers=[scatter_layer],
        initial_view_state=view_state,
        tooltip={"text": "Department: {department}\nIssue ID: {id}"}
    )
    
    # Display the map in Streamlit.
    st.pydeck_chart(deck)
    
    # Display the legend below the map.
    display_map_legend(department_color_mapping)
