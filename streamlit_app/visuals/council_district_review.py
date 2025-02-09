import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import json
import re

@st.cache_data
def load_council_geojson():
    """Load the City Council Districts GeoJSON file."""
    with open("exports/City_Council_Districts.geojson", "r", encoding="utf-8") as f:
        return json.load(f)

def hex_to_rgba(color, opacity=0.7):
    """Convert a hex color or an rgb/rgba string to an rgba string with the given opacity.

    If the input starts with '#' it is assumed to be a hex color.
    If it starts with 'rgb', it is parsed and the opacity is overridden.
    """
    if color.startswith("#"):
        hex_color = color.lstrip('#')
        # Expand shorthand hex (e.g. "fff") to full form ("ffffff")
        if len(hex_color) == 3:
            hex_color = ''.join([c*2 for c in hex_color])
        try:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
        except ValueError:
            # Fallback: return the original color if conversion fails
            return color
        return f"rgba({r}, {g}, {b}, {opacity})"
    elif color.startswith("rgb"):
        # Extract numeric values from the string
        nums = re.findall(r"[\d.]+", color)
        if len(nums) >= 3:
            r, g, b = nums[:3]
            return f"rgba({r}, {g}, {b}, {opacity})"
        else:
            return color
    else:
        # Fallback if the color format is unrecognized.
        return color

def display_council_map(filtered_df):
    """Display a map of council districts, shading each district by its issue count."""
    st.markdown("### Council Districts Map")
    
    # Load council districts GeoJSON data
    council_geojson = load_council_geojson()
    
    # Build a list of district features with some useful properties.
    # The 'dist_id' here should match the 'council_district' column in your dataframe.
    council_map_data = []
    for feature in council_geojson["features"]:
        council_map_data.append({
            "geometry": feature["geometry"],
            "dist_id": feature["properties"].get("dist_id", "Unknown"),
            "district": feature["properties"].get("district", "Unknown"),
            "councilmember": feature["properties"].get("councilmember", "Unknown")
        })
    
    # Group the issues by council district
    issue_counts = filtered_df.groupby("council_district").size().reset_index(name="issue_count")
    
    # Merge issue counts with the council map data.
    # Create a lookup dictionary keyed by the district id (dist_id)
    council_map_data_dict = {feature["dist_id"]: feature for feature in council_map_data}
    for _, row in issue_counts.iterrows():
        district_id = row["council_district"]
        if district_id in council_map_data_dict:
            council_map_data_dict[district_id]["issue_count"] = row["issue_count"]
    
    # Set default issue_count to 0 for any district without issues
    for feature in council_map_data:
        feature["issue_count"] = feature.get("issue_count", 0)
    
    # Find the maximum issue count (avoiding division by zero)
    max_issue_count = max([f["issue_count"] for f in council_map_data] or [1])
    
    # Define a color scale where higher issue counts are shown in red.
    # We use the reversed RdYlGn scale so that red is at the high end.
    colorscale = px.colors.diverging.RdYlGn[::-1]
    num_colors = len(colorscale)
    
    # Create a Plotly figure and add a trace for each district polygon
    fig = go.Figure()
    
    for feature in council_map_data:
        # Use a transparent fill if there are no issues
        if feature["issue_count"] == 0:
            color = "rgba(0,0,0,0)"
        else:
            # Normalize the issue count to choose a color from the scale
            normalized = feature["issue_count"] / max_issue_count
            color_idx = int(normalized * (num_colors - 1))
            base_color = colorscale[color_idx]
            color = hex_to_rgba(base_color, opacity=0.5)
    
        geometry = feature["geometry"]
        # Handle both Polygon and MultiPolygon geometries
        if geometry["type"] == "Polygon":
            for polygon in geometry["coordinates"]:
                # Ensure we are dealing with a list of coordinate points
                if isinstance(polygon[0], list):
                    fig.add_trace(go.Scattermapbox(
                        lon=[point[0] for point in polygon],
                        lat=[point[1] for point in polygon],
                        mode="lines",
                        fill="toself",
                        fillcolor=color,
                        line=dict(width=2, color='black'),
                        hovertemplate=(
                            "District: %{customdata[0]}<br>" +
                            "Council Member: %{customdata[1]}<br>" +
                            "Issue Count: %{customdata[2]}<extra></extra>"
                        ),
                        customdata=[[feature["district"],
                                     feature["councilmember"],
                                     feature["issue_count"]]] * len(polygon)
                    ))
        elif geometry["type"] == "MultiPolygon":
            for multi_polygon in geometry["coordinates"]:
                for polygon in multi_polygon:
                    if isinstance(polygon[0], list):
                        fig.add_trace(go.Scattermapbox(
                            lon=[point[0] for point in polygon],
                            lat=[point[1] for point in polygon],
                            mode="lines",
                            fill="toself",
                            fillcolor=color,
                            line=dict(width=2, color='black'),
                            hovertemplate=(
                                "District: %{customdata[0]}<br>" +
                                "Council Member: %{customdata[1]}<br>" +
                                "Issue Count: %{customdata[2]}<extra></extra>"
                            ),
                            customdata=[[feature["district"],
                                         feature["councilmember"],
                                         feature["issue_count"]]] * len(polygon)
                        ))
    
    # Configure the map layout (centered over Tacoma in this example)
    fig.update_layout(
        mapbox=dict(
            style="open-street-map",
            center=dict(lat=47.2529, lon=-122.4443),
            zoom=11
        ),
        margin=dict(l=0, r=0, t=0, b=0)
    )
    
    st.plotly_chart(fig, use_container_width=True)
