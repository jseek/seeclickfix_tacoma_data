import streamlit as st
import plotly.express as px

def render_scatter_map(issue_mapping_df):
    fig = px.scatter_mapbox(
        issue_mapping_df, 
        lat="lat", lon="lng", 
        hover_data=["description", "status"],
        mapbox_style="open-street-map", 
        zoom=st.session_state.map_zoom,  # Keep last zoom level
        center={"lat": st.session_state.map_center_lat, "lon": st.session_state.map_center_lon},  # Keep last center
        color_discrete_sequence=["yellow"],  # Use a consistent color
    )

    fig.update_traces(
        marker=dict(size=6, opacity=0.8),  # Adjust marker appearance
        cluster=dict(enabled=True)  # Enable clustering
    )

    return fig
