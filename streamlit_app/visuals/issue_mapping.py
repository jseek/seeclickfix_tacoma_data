import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from streamlit_app.visuals.maps.heatmap import render_heatmap
from streamlit_app.visuals.maps.scatter_map import render_scatter_map

def display_map(issue_mapping_df):
    """Displays the interactive map section with a toggle for Heatmap vs. Clustered Issues."""

    st.subheader("Tacoma 311 Issues Map")
    st.markdown("Toggle between the **Clustered Issue View** and **Heatmap**.")

    # Initialize session state for map settings
    if "map_zoom" not in st.session_state:
        st.session_state.map_zoom = 10
    if "map_center_lat" not in st.session_state:
        st.session_state.map_center_lat = issue_mapping_df['lat'].mean()
    if "map_center_lon" not in st.session_state:
        st.session_state.map_center_lon = issue_mapping_df['lng'].mean()

    # Toggle between views
    show_heatmap = st.toggle("Show Heatmap", value=False)

    # If Heatmap is selected
    if show_heatmap:
        fig = render_heatmap(issue_mapping_df)
    else:
        fig = render_scatter_map(issue_mapping_df)

    # Apply session state zoom & center
    fig.update_layout(
        mapbox_style="open-street-map",
        mapbox_center={"lat": st.session_state.map_center_lat, "lon": st.session_state.map_center_lon},
        mapbox_zoom=st.session_state.map_zoom
    )

    # Render the chart
    st.plotly_chart(fig, use_container_width=True)

    # Manually update the stored map state after rendering
    if fig.layout.mapbox.zoom is not None:
        st.session_state.map_zoom = fig.layout.mapbox.zoom
    if fig.layout.mapbox.center is not None:
        st.session_state.map_center_lat = fig.layout.mapbox.center.lat
        st.session_state.map_center_lon = fig.layout.mapbox.center.lon
