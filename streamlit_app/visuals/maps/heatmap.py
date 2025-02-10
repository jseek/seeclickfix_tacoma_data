import streamlit as st
import plotly.graph_objects as go

def render_heatmap(issue_mapping_df):
    # Let the user choose which summary to display
    unique_summaries = issue_mapping_df['summary'].unique()
    selected_summary = st.selectbox("Select Summary", unique_summaries)
    
    # Filter the DataFrame for the selected summary
    filtered_df = issue_mapping_df[issue_mapping_df['summary'] == selected_summary]
    
    # Allow the user to adjust the density radius
    radius_value = st.slider(
        "Heatmap Radius", 
        min_value=1, max_value=50, 
        value=2, step=1
    )
    
    # Create the density heatmap
    fig = go.Figure(go.Densitymapbox(
        lat=filtered_df['lat'],
        lon=filtered_df['lng'],
        z=[1] * len(filtered_df),  # Each request is given equal weight
        radius=radius_value,
        colorscale="Viridis"
    ))
    
    # Center the map on the filtered points (if any)
    if not filtered_df.empty:
        center_lat = filtered_df['lat'].mean()
        center_lon = filtered_df['lng'].mean()
    else:
        # If no points exist, default to a global center (or choose your own)
        center_lat, center_lon = 0, 0
    
    fig.update_layout(
        mapbox=dict(
            style="open-street-map",
            center={'lat': center_lat, 'lon': center_lon},
            zoom=10  # Adjust as needed for your data
        ),
        margin={"r": 0, "t": 0, "l": 0, "b": 0}
    )
    
    return fig