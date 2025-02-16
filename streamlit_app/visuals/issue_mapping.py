import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from streamlit_app.visuals.maps.heatmap import render_heatmap
from streamlit_app.visuals.maps.scatter_map import render_scatter_map
import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
import pydeck as pdk
import random

def display_map(issue_mapping_df):
    """Displays the interactive map section with buttons for Clustered vs. Heatmap views."""

    st.subheader("Tacoma 311 Issues Map")
    st.markdown("Select between the **Clustered Issue View** and **Heatmap**.")

    # Initialize session state for map settings
    if "map_zoom" not in st.session_state:
        st.session_state.map_zoom = 10
    if "map_center_lat" not in st.session_state:
        st.session_state.map_center_lat = issue_mapping_df['lat'].mean()
    if "map_center_lon" not in st.session_state:
        st.session_state.map_center_lon = issue_mapping_df['lng'].mean()

    # Use radio buttons for selection. The horizontal layout makes the options appear side by side.
    map_view = st.radio(
        "Map View",
        options=["Clustered", "Heatmap"],
        index=1,  # Default to Heatmap (index 1)
        horizontal=True
    )

    # Choose the appropriate rendering function based on the selection.
    if map_view == "Heatmap":
        fig = render_heatmap(issue_mapping_df)
    else:
        fig = render_scatter_map(issue_mapping_df)

    # Apply session state zoom & center settings.
    fig.update_layout(
        mapbox_style="open-street-map",
        mapbox_center={"lat": st.session_state.map_center_lat, "lon": st.session_state.map_center_lon},
        mapbox_zoom=st.session_state.map_zoom
    )

    # Render the chart
    st.plotly_chart(fig, use_container_width=True)

    # Manually update the stored map state after rendering.
    if fig.layout.mapbox.zoom is not None:
        st.session_state.map_zoom = fig.layout.mapbox.zoom
    if fig.layout.mapbox.center is not None:
        st.session_state.map_center_lat = fig.layout.mapbox.center.lat
        st.session_state.map_center_lon = fig.layout.mapbox.center.lon

def create_hotspots_map(df, eps=0.005, min_samples=5):
    """
    Creates a Pydeck map visualizing emerging hotspots using DBSCAN clustering.
    
    Parameters:
    - df: A pandas DataFrame that must contain 'lat' and 'lng' columns.
    - eps: DBSCAN's epsilon parameter (in degrees). Default is 0.005.
    - min_samples: DBSCAN's minimum number of samples. Default is 5.
    
    Returns:
    - deck_chart: A pydeck.Deck object with the clustered points, or None if an error occurred.
    - df: The updated DataFrame with a 'cluster' column.
    """
    # Ensure the DataFrame contains the necessary columns
    if 'lat' not in df.columns or 'lng' not in df.columns:
        st.error("DataFrame must contain 'lat' and 'lng' columns.")
        return None, df

    # Convert lat/lng to numeric and drop any rows with missing values
    df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
    df['lng'] = pd.to_numeric(df['lng'], errors='coerce')
    df = df.dropna(subset=['lat', 'lng'])

    # If the DataFrame is empty after cleaning, return None
    if df.empty:
        st.warning("No valid latitude/longitude data available.")
        return None, df

    # Extract coordinates and apply DBSCAN clustering
    coords = df[['lat', 'lng']].to_numpy()
    db = DBSCAN(eps=eps, min_samples=min_samples)
    labels = db.fit_predict(coords)

    # If no clusters are found (only noise), warn the user but still proceed
    if len(set(labels)) <= 1:
        st.warning("No clusters detected. Try adjusting the DBSCAN parameters.")

    # Add the cluster column (even if it’s all noise)
    df['cluster'] = labels.astype(int)

    # Map each cluster label to a color for visualization
    unique_labels = np.unique(labels)
    colors = {}
    for label in unique_labels:
        if label == -1:  # Noise points
            colors[label] = [150, 150, 150, 140]  # RGBA for noise
        else:
            colors[label] = [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), 140]
    
    # Assign colors based on the cluster value
    df['color'] = df['cluster'].map(lambda x: colors.get(int(x), [0, 0, 0, 140]))
    df['color'] = df['color'].apply(lambda x: [int(i) for i in x])  # Ensure integer list
    df = df.astype({'cluster': 'int'})  # Ensure clusters are integers

    # Debug: Display a preview of the clustered data
    st.write("Clustered Data Preview:", df.head())

    # Convert DataFrame to a list of dictionaries (JSON-serializable)
    data_records = df[['lng', 'lat', 'cluster', 'color']].to_dict(orient="records")

    # Define a ScatterplotLayer for the map
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=data_records,
        get_position="[lng, lat]",
        get_radius=100,
        get_fill_color="color",
        pickable=True
    )

    # Center the view on the data's midpoint
    midpoint = (df['lat'].mean(), df['lng'].mean())
    view_state = pdk.ViewState(
        latitude=midpoint[0],
        longitude=midpoint[1],
        zoom=11,
        pitch=0
    )

    # Create the Pydeck deck
    deck_chart = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={"text": "Cluster: {cluster}"}
    )
    
    # Always return a tuple (deck_chart, df)
    return deck_chart, df