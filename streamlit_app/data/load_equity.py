import pandas as pd
import streamlit as st
import json

@st.cache_data
def load_equity_population():
    """Loads equity population data from GeoJSON."""
    with open("exports/Equity_Index_2024_(Tacoma).geojson", "r", encoding="utf-8") as f:
        data = json.load(f)

    equity_population_df = pd.DataFrame([
        {
            "equity_objectid": feature["properties"].get("objectid"),
            "population": feature["properties"].get("population", 0)  # Default to 0 if missing
        }
        for feature in data["features"]
    ])
    
    return equity_population_df
