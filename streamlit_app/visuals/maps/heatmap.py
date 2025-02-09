import streamlit as st
import plotly.graph_objects as go

def render_heatmap(issue_mapping_df):
    radius_value = st.slider(
        "Heatmap Radius", 
        min_value=1, max_value=50, 
        value=2, step=1
    )

    fig = go.Figure(go.Densitymapbox(
        lat=issue_mapping_df['lat'],
        lon=issue_mapping_df['lng'],
        z=[1] * len(issue_mapping_df),  # Each point contributes equally
        radius=radius_value,  # User-controlled radius
        colorscale="Viridis"
    ))

    return fig
