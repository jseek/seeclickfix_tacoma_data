import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import json
import re
import pandas as pd

@st.cache_data
def load_equity_geojson():
    """Load the Equity Index GeoJSON file."""
    with open("exports/Equity_Index_2024_(Tacoma).geojson", "r", encoding="utf-8") as f:
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

def get_equity_data(filtered_df):
    """
    Process the equity geojson data and merge issue counts from filtered_df.
    Returns a list of dictionaries, one per feature, with computed fields.
    """
    equity_geojson = load_equity_geojson()

    # Extract polygon data and properties
    equity_data = []
    for feature in equity_geojson["features"]:
        data = {
            "equity_id": feature["properties"].get("objectid", "Unknown"),
            "population": feature["properties"].get("population", 1),  # Avoid division by zero
            "equityindex": feature["properties"].get("equityindex"),
            "equityindexvalue": feature["properties"].get("equityindexvalue"),
            "livabilityindex": feature["properties"].get("livabilityindex"),
            "livabilityindexvalue": feature["properties"].get("livabilityindexvalue"),
            "accessibilityindex": feature["properties"].get("accessibilityindex"),
            "accessibilityindexvalue": feature["properties"].get("accessibilityindexvalue"),
            "economicindex": feature["properties"].get("economicindex"),
            "economicindexvalue": feature["properties"].get("economicindexvalue"),
            "educationindex": feature["properties"].get("educationindex"),
            "educationindexvalue": feature["properties"].get("educationindexvalue"),
            "environmentalindex": feature["properties"].get("environmentalindex"),
            "environmentalindexvalue": feature["properties"].get("environmentalindexvalue"),
            "averagepavementcondition": feature["properties"].get("averagepavementcondition"),
            "healthyfoodavailability": feature["properties"].get("healthyfoodavailability"),
            "householdvehicleaccess": feature["properties"].get("householdvehicleaccess"),
            "householdswithinternet": feature["properties"].get("householdswithinternet"),
            "parksopenspace": feature["properties"].get("parksopenspace"),
            "communityparks": feature["properties"].get("communityparks"),
            "regionalparks": feature["properties"].get("regionalparks"),
            "neighborhoodparks": feature["properties"].get("neighborhoodparks"),
            "transitaccessscore": feature["properties"].get("transitaccessscore"),
            "voterparticipationrate": feature["properties"].get("voterparticipationrate"),
            "sidewalksandbikeways": feature["properties"].get("sidewalksandbikeways"),
            "f200__of_poverty": feature["properties"].get("f200__of_poverty"),
            "povertyrate": feature["properties"].get("povertyrate"),
            "jobsindex": feature["properties"].get("jobsindex"),
            "jobsdensity": feature["properties"].get("jobsdensity"),
            "medianhouseholdincome": feature["properties"].get("medianhouseholdincome"),
            "employmentrate": feature["properties"].get("employmentrate"),
            "averagestudentmobility": feature["properties"].get("averagestudentmobility"),
            "percent25yearoldswithbachelorsd": feature["properties"].get("percent25yearoldswithbachelorsd"),
            "averagetestingproficiency": feature["properties"].get("averagetestingproficiency"),
            "educationalattainmentindex": feature["properties"].get("educationalattainmentindex"),
            "highschoolgraduationrate": feature["properties"].get("highschoolgraduationrate"),
            "kindergartenreadinessrate": feature["properties"].get("kindergartenreadinessrate"),
            "dieselemissions": feature["properties"].get("dieselemissions"),
            "ozoneconcentration": feature["properties"].get("ozoneconcentration"),
            "pm25particulates": feature["properties"].get("pm25particulates"),
            "toxicreleasesfromfacilities": feature["properties"].get("toxicreleasesfromfacilities"),
            "proximitytoheavytrafficroadways": feature["properties"].get("proximitytoheavytrafficroadways"),
            "urbanheatislandeffect": feature["properties"].get("urbanheatislandeffect"),
            "urbantreecanopy": feature["properties"].get("urbantreecanopy"),
            "costburdenedhouseholds": feature["properties"].get("costburdenedhouseholds"),
            "ownercostburden": feature["properties"].get("ownercostburden"),
            "rentercostburden": feature["properties"].get("rentercostburden"),
            "owneroccupiedunits": feature["properties"].get("owneroccupiedunits"),
            "medianhomevalue": feature["properties"].get("medianhomevalue"),
            "pedestrianbicyclistcrashes": feature["properties"].get("pedestrianbicyclistcrashes"),
            "tacomacrimerisk": feature["properties"].get("tacomacrimerisk"),
            "tacomapersonalcrime": feature["properties"].get("tacomapersonalcrime"),
            "tacomapropertycrime": feature["properties"].get("tacomapropertycrime"),
            "insuredrate": feature["properties"].get("insuredrate"),
            "averagelifeexpectancy": feature["properties"].get("averagelifeexpectancy"),
            "population": feature["properties"].get("population"),
            "populationdensity": feature["properties"].get("populationdensity"),
            "limitedenglish": feature["properties"].get("limitedenglish"),
            "populationunder18": feature["properties"].get("populationunder18"),
            "population18to64": feature["properties"].get("population18to64"),
            "population65andabove": feature["properties"].get("population65andabove"),
            "americanindianoralaskannative": feature["properties"].get("americanindianoralaskannative"),
            "asian": feature["properties"].get("asian"),
            "blackorafricanamerican": feature["properties"].get("blackorafricanamerican"),
            "hispanicorlatino": feature["properties"].get("hispanicorlatino"),
            "nativehawaiianorpacificislander": feature["properties"].get("nativehawaiianorpacificislander"),
            "otherrace": feature["properties"].get("otherrace"),
            "twoormoreraces": feature["properties"].get("twoormoreraces"),
            "white": feature["properties"].get("white"),
            "peopleofcolor": feature["properties"].get("peopleofcolor"),
            "peopleofcolor_population": feature["properties"].get("peopleofcolor") * feature["properties"].get("population"),
            "geometry": feature["geometry"]
        }
        equity_data.append(data)

    # Compute issue counts grouped by equity_objectid
    issue_counts = filtered_df.groupby("equity_objectid").size().reset_index(name="issue_count")
    equity_data_dict = {d["equity_id"]: d for d in equity_data}
    for _, row in issue_counts.iterrows():
        equity_id = row["equity_objectid"]
        if equity_id in equity_data_dict:
            equity_data_dict[equity_id]["issue_count"] = row["issue_count"]

    # Compute additional fields
    for d in equity_data:
        d["issue_count"] = d.get("issue_count", 0)
        # For convenience, compute issues per capita (if needed elsewhere)
        d["issues_per_capita"] = (d["issue_count"] / d["population"]) if d["population"] > 0 else 0

    return equity_data

def display_equity_map(filtered_df):
    """Display the equity index map with issue density."""
    st.markdown("### Equity Index Map")

    # Let the user select the metric to highlight
    highlight_option = st.selectbox(
        "Highlight map by:",
        [
            "Issues per Capita",
            "Issues per People of Color Population",
            "Weighted Issue Count"
        ],
        index=0
    )

    equity_data = get_equity_data(filtered_df)

    # Compute the highlight value for each feature based on selection
    for d in equity_data:
        if highlight_option == "Issues per Capita":
            d["highlight_value"] = d["issues_per_capita"]
        elif highlight_option == "Issues per People of Color Population":
            d["highlight_value"] = (d["issue_count"] / d["peopleofcolor_population"]
                                    if d["peopleofcolor_population"] > 0 else 0)
        elif highlight_option == "Weighted Issue Count":
            # Multiply issue count by peopleofcolor fraction.
            d["highlight_value"] = d["issue_count"] * d["peopleofcolor"]

    max_highlight = max([d["highlight_value"] for d in equity_data if d["issue_count"] > 0] or [1])

    colorscale = px.colors.diverging.RdYlGn[::-1]  # Reverse so red indicates higher values
    num_colors = len(colorscale)

    hover_template = (
        "Equity ID: %{customdata[0]}<br>"
        "Population: %{customdata[1]:,.0f}<br>"
        "Issue Count: %{customdata[2]:,.0f}<br>"
        "Issues per Capita: %{customdata[3]:.4f}<br>"
        "People of Color: %{customdata[4]:.2%}<br>"
        "People of Color Population: %{customdata[5]:,.0f}<br>"
        f"Highlight Value ({highlight_option}): " + "%{customdata[6]:.4f}<extra></extra>"
    )

    fig = go.Figure()

    for d in equity_data:
        if d["issue_count"] == 0:
            color = "rgba(0,0,0,0)"
        else:
            color_idx = int((d["highlight_value"] / max_highlight) * (num_colors - 1))
            base_color = colorscale[color_idx]
            color = hex_to_rgba(base_color, opacity=0.5)

        custom_data = [
            d["equity_id"],
            d["population"],
            d["issue_count"],
            d["issues_per_capita"],
            d["peopleofcolor"],
            d["peopleofcolor_population"],
            d["highlight_value"]
        ]

        geom = d["geometry"]
        if geom["type"] == "Polygon":
            for polygon in geom["coordinates"]:
                if isinstance(polygon[0], list):
                    fig.add_trace(go.Scattermapbox(
                        name=d["equity_id"],
                        lon=[point[0] for point in polygon],
                        lat=[point[1] for point in polygon],
                        mode="lines",
                        fill="toself",
                        fillcolor=color,
                        line=dict(width=2, color='black'),
                        hovertemplate=hover_template,
                        customdata=[custom_data] * len(polygon)
                    ))
        elif geom["type"] == "MultiPolygon":
            for multi_polygon in geom["coordinates"]:
                for polygon in multi_polygon:
                    if isinstance(polygon[0], list):
                        fig.add_trace(go.Scattermapbox(
                            name=d["equity_id"],
                            lon=[point[0] for point in polygon],
                            lat=[point[1] for point in polygon],
                            mode="lines",
                            fill="toself",
                            fillcolor=color,
                            line=dict(width=2, color='black'),
                            hovertemplate=hover_template,
                            customdata=[custom_data]
                        ))

    fig.update_layout(
        mapbox=dict(
            style="open-street-map",
            center=dict(lat=47.2529, lon=-122.4443),
            zoom=11
        ),
        margin=dict(l=0, r=0, t=0, b=0)
    )

    if equity_data:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No equity index data available to display on the map.")

def display_equity_scatterplot(filtered_df):
    """
    Display a scatterplot where the x-axis is the People of Color value (as a percent)
    and the y-axis is the count of issues.
    """
    st.markdown("### Scatterplot: People of Color vs. Issue Count")
    
    equity_data = get_equity_data(filtered_df)
    
    # Create a dataframe for the scatter plot
    # Compute People of Color percentage for display (peopleofcolor * 100)
    df = pd.DataFrame(equity_data)
    
    # Use Plotly Express to create a scatter plot
    fig = px.scatter(
        df,
        x="peopleofcolor_population",
        y="issue_count",
        hover_data=["equity_id", "population"],
        labels={
            "peopleofcolor_population": "POC Population",
            "issue_count": "Issue Count"
        },
        title="Issue Count by POC Counts"
    )
    
    st.plotly_chart(fig, use_container_width=True)