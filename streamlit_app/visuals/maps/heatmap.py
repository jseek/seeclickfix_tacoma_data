import streamlit as st
import plotly.graph_objects as go
import hashlib
import pandas as pd

def render_heatmap(issue_mapping_df):
    df_hash = hashlib.md5(pd.util.hash_pandas_object(issue_mapping_df).values).hexdigest()
    
    radius_value = st.slider(
        "Select radius for heatmap",
        min_value=1, 
        max_value=100, 
        value=2,
        key=f"heatmap_radius_slider_{df_hash}"  # Unique key per dataset
    )

    fig = go.Figure(go.Densitymapbox(
        lat=issue_mapping_df['lat'],
        lon=issue_mapping_df['lng'],
        z=[1] * len(issue_mapping_df),  # Each point contributes equally
        radius=radius_value,  # User-controlled radius
        colorscale="Viridis"
    ))

    return fig