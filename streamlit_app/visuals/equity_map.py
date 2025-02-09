import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import json

@st.cache_data
def load_equity_geojson():
    """Load the Equity Index GeoJSON file."""
    with open("exports/Equity_Index_2024_(Tacoma).geojson", "r", encoding="utf-8") as f:
        return json.load(f)

def display_equity_map(filtered_df):
    """Function to compute and display the equity index map with issue density."""
    st.markdown("### Equity Index Map")

    # Load data
    equity_geojson = load_equity_geojson()

    # Extract polygon coordinates and properties
    equity_map_data = []
    for feature in equity_geojson["features"]:
        equity_map_data.append({
            "geometry": feature["geometry"],
            "equity_id": feature["properties"].get("objectid", "Unknown"),
            "population": feature["properties"].get("population", 1)  # Default to 1 to avoid division by zero
        })

    # Compute issue counts grouped by equity_objectid
    issue_counts = filtered_df.groupby("equity_objectid").size().reset_index(name="issue_count")

    # Merge issue counts with equity map data
    equity_map_data_dict = {f["equity_id"]: f for f in equity_map_data}
    for _, row in issue_counts.iterrows():
        equity_id = row["equity_objectid"]
        if equity_id in equity_map_data_dict:
            equity_map_data_dict[equity_id]["issue_count"] = row["issue_count"]

    # Set default issue_count to 0 if not present and compute issues per capita
    for feature in equity_map_data:
        feature["issue_count"] = feature.get("issue_count", 0)
        feature["issues_per_capita"] = feature["issue_count"] / feature["population"] if feature["population"] > 0 else 0

    # Get max issues per capita for normalization
    max_issues_per_capita = max([f["issues_per_capita"] for f in equity_map_data] or [1])

    # Define color scale (Green → Yellow → Red, where Red is the worst)
    colorscale = px.colors.diverging.RdYlGn[::-1]  # Reverse to make red the highest
    num_colors = len(colorscale)

    # Create the map
    fig = go.Figure()

    for feature in equity_map_data:
        color_idx = int((feature["issues_per_capita"] / max_issues_per_capita) * (num_colors - 1))
        color = colorscale[color_idx]

        if feature["geometry"]["type"] == "Polygon":
            for polygon in feature["geometry"]["coordinates"]:
                if isinstance(polygon[0], list):  # Ensure it's a list of coordinates
                    fig.add_trace(go.Scattermapbox(
                        lon=[point[0] for point in polygon],
                        lat=[point[1] for point in polygon],
                        mode="lines",
                        fill="toself",
                        fillcolor=color,
                        line=dict(width=2, color='black'),
                        hovertemplate=(
                            "Equity ID: %{customdata[0]}<br>"
                            "Population: %{customdata[1]:,.0f}<br>"
                            "Issue Count: %{customdata[2]:,.0f}<br>"
                            "Issues per Capita: %{customdata[3]:.4f}<extra></extra>"
                        ),
                        customdata=[[feature['equity_id'], feature['population'], feature['issue_count'], feature['issues_per_capita']]] * len(polygon)
                    ))
        elif feature["geometry"]["type"] == "MultiPolygon":
            for multi_polygon in feature["geometry"]["coordinates"]:
                for polygon in multi_polygon:
                    if isinstance(polygon[0], list):  # Ensure it's a list of coordinates
                        fig.add_trace(go.Scattermapbox(
                            lon=[point[0] for point in polygon],
                            lat=[point[1] for point in polygon],
                            mode="lines",
                            fill="toself",
                            fillcolor=color,
                            line=dict(width=2, color='black'),
                            hovertemplate=(
                                "Equity ID: %{customdata[0]}<br>"
                                "Population: %{customdata[1]:,.0f}<br>"
                                "Issue Count: %{customdata[2]:,.0f}<br>"
                                "Issues per Capita: %{customdata[3]:.4f}<extra></extra>"
                            ),
                            customdata=[[feature['equity_id'], feature['population'], feature['issue_count'], feature['issues_per_capita']]]
                        ))

    fig.update_layout(
        mapbox=dict(
            style="open-street-map",
            center=dict(lat=47.2529, lon=-122.4443),
            zoom=11
        ),
        margin=dict(l=0, r=0, t=0, b=0)
    )

    if equity_map_data:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No equity index data available to display on the map.")
