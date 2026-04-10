"""
Market-Feasible Units Dashboard - Main Streamlit Application
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo

# Import local modules
from data_loader import fetch_data_from_api, process_aggregation_data
from charts import (
    create_multi_scenario_stacked_chart,
    create_total_feasibility_chart_grouped,
    create_location_grouped_chart,
)
from colors import (
    total_feasibility_color,
    income_bracket_colors,
    bedroom_count_colors,
    parking_type_colors,
    density_colors,
    far_colors,
    unit_type_colors,
    tcac_colors,
    fire_risk_colors,
)
from ui_helpers import apply_embed_styles, render_subheader, render_title


# ============================================================================
# Main Dashboard
# ============================================================================

st.set_page_config(page_title="Market-Feasible Units Dashboard", layout="wide")

try:
    # Check for simulation ID parameters
    params = st.query_params

    is_embedded = apply_embed_styles(params)

    # Get project ID from query params
    project_id = params.get("project_id")
    if not project_id:
        st.error("❌ No project_id provided")
        st.stop()

    # Get simulation IDs from query params
    simulation_ids_param = params.get("simulation_ids")
    if not simulation_ids_param:
        st.error("❌ No simulation IDs provided")
        st.stop()

    # Split by comma if multiple IDs are provided
    simulation_ids = [sid.strip() for sid in simulation_ids_param.split(",")]

    # Fetch data from API
    api_response = fetch_data_from_api(simulation_ids, project_id)
    if not api_response:
        st.error(
            "Failed to fetch data from API. Please check your simulation IDs and try again."
        )
        st.stop()

except Exception as e:
    st.error("❌ An error occurred while loading the dashboard")
    st.error(f"Error: {str(e)}")
    st.info(
        "**Please ensure you provide both project_id and simulation_ids in the URL.**\n\n"
        "Example: `?project_id=StandardCalifornia&simulation_ids=-Ogiwnj-fYy4wjWPOn8-,-Ogiwo-hmQWX6i7THCN2`"
    )
    st.stop()

# Load all data from API response
all_data = []
all_metadata = []

# The API returns data as a dict with simulation IDs as keys
# Each value contains 'metadata' and 'data' properties
for i, sim_id in enumerate(simulation_ids):
    if sim_id in api_response:
        sim_response = api_response[sim_id]

        # Extract metadata
        metadata = sim_response.get("metadata", {})
        all_metadata.append(
            {
                "simulation_id": sim_id,
                "name": metadata.get("name", f"Scenario {i+1}"),
                "description": metadata.get("description", ""),
                "createDate": metadata.get("createDate", ""),
            }
        )

        # Extract data (now a list of data objects)
        data_list = sim_response.get("data", [])
        if data_list and len(data_list) > 0:
            raw_data = data_list[0]
            # Process the raw data using the scenario name from metadata
            scenario_name = metadata.get("name", f"Scenario {i+1}")
            processed_data = process_aggregation_data(raw_data, scenario_name)
            if processed_data:
                all_data.append(processed_data)

# Check if we successfully loaded any data
if not all_data:
    st.error("Failed to load any data. Please check the URLs and try again.")
    st.stop()

# Display metadata table at the top
if not is_embedded:
    render_title("Market-Feasible Units Dashboard", is_embedded)

if all_metadata and not is_embedded:
    render_subheader("Simulation Details", is_embedded)

    # Format the metadata for display
    metadata_display = []
    for meta in all_metadata:
        # Format the date nicely
        create_date = meta["createDate"]
        if create_date:
            try:
                dt = datetime.fromisoformat(create_date.replace("Z", "+00:00"))
                # Convert to Pacific time
                pacific_dt = dt.astimezone(ZoneInfo("America/Los_Angeles"))
                formatted_date = pacific_dt.strftime("%B %d, %Y at %I:%M %p PT")
            except:
                formatted_date = create_date
        else:
            formatted_date = "N/A"

        metadata_display.append(
            {
                "Simulation Name": meta["name"],
                "Description": meta["description"] if meta["description"] else "N/A",
                "Created": formatted_date,
            }
        )

    # Create and display the metadata dataframe
    df_metadata = pd.DataFrame(metadata_display)
    st.dataframe(df_metadata, hide_index=True, width="stretch")

    st.markdown("---")

# Chart 1: Feasibility Summary
render_title("Feasibility Summary2", is_embedded)
total_data_dict = {"Total Units": [], "Net Units": [], "Affordable Units": []}
scenario_names = []
for i, data in enumerate(all_data):
    # Set default scenario names if not provided in data
    scenario_name = data.get("scenario_name", f"Scenario {i+1}")
    # Truncate long names for chart labels
    if len(scenario_name) > 30:
        truncated_name = scenario_name[:27] + "..."
    else:
        truncated_name = scenario_name
    scenario_names.append(truncated_name)
    total_data_dict["Total Units"].append(data["total_units"])
    total_data_dict["Net Units"].append(data["net_units"])
    total_data_dict["Affordable Units"].append(data["affordable_units"])

df_total = pd.DataFrame(total_data_dict, index=scenario_names)

# Create grouped bar chart for total feasibility
fig_total = create_total_feasibility_chart_grouped(
    scenario_names, total_data_dict, total_feasibility_color
)

st.plotly_chart(fig_total, width="stretch")
render_subheader("Feasibility Data", is_embedded)
st.dataframe(df_total.T, width="stretch")

st.markdown("---")

# Chart 2: Units by Location
render_title("Units by Location", is_embedded)

# All possible location configs (key, display_name, color)
all_location_configs = [
    # Transit/Transportation
    ("hq_transit_area", "HQ Transit Area", "#5DBDB4"),
    ("tod_area", "TOD Area", "#6B9BD1"),
    ("quarter_mile_of_rail", "Quarter Mile of Rail", "#6FB573"),
    ("half_mile_of_rail_or_brt", "Half Mile of Rail or BRT", "#F4C04E"),
    ("half_mile_of_brt", "Half Mile of BRT", "#F07D4A"),
    ("near_transit", "Near Transit", "#D66E6C"),
    # Urban characteristics
    ("urbanized", "Urbanized", "#5DBDB4"),
    ("walkable", "Walkable", "#6B9BD1"),
    ("mfte", "MFTE", "#6FB573"),
    ("industrial", "Industrial", "#F4C04E"),
    ("historic_district", "Historic District", "#F07D4A"),
    # Environmental/Geological hazards
    ("critical", "Critical", "#D66E6C"),
    ("geological", "Geological", "#5DBDB4"),
    ("seismic", "Seismic", "#6B9BD1"),
    ("fault_zone", "Fault Zone", "#6FB573"),
    ("landslide", "Landslide", "#F4C04E"),
    ("steep_slope", "Steep Slope", "#F07D4A"),
    ("erosion", "Erosion", "#D66E6C"),
    ("wui", "WUI", "#5DBDB4"),
    ("tsunami", "Tsunami", "#6B9BD1"),
    ("sea_level_rise", "Sea Level Rise", "#6FB573"),
    # Habitat
    ("habitat", "Habitat", "#F4C04E"),
    ("habitat_priority", "Habitat Priority", "#F07D4A"),
    # Agriculture / Water
    ("agriculture", "Agriculture", "#6FB573"),
    ("aquifer_recharge", "Aquifer Recharge", "#5DBDB4"),
]

# Filter to only include location configs where at least one scenario has data
location_configs = []
for config in all_location_configs:
    key = config[0]
    # Check if any scenario has non-zero data for this location
    has_data = any(data["location_data"].get(key, 0) > 0 for data in all_data)
    if has_data:
        location_configs.append(config)

# Only show location chart if there are location attributes with data
if location_configs:
    # Chart with Total Units included
    fig_location_with_total = create_location_grouped_chart(
        all_data, location_configs, include_total=True
    )
    st.plotly_chart(fig_location_with_total, width="stretch")

    # Create dataframe for location data including total
    location_data_with_total = {"Total Units": []}
    for config in location_configs:
        location_data_with_total[config[1]] = []

    for data in all_data:
        location_data_with_total["Total Units"].append(data["total_units"])
        for config in location_configs:
            location_data_with_total[config[1]].append(data["location_data"][config[0]])

    df_location_with_total = pd.DataFrame(
        location_data_with_total, index=scenario_names
    )
    render_subheader("Location Data", is_embedded)
    st.dataframe(df_location_with_total.T, width="stretch")

st.markdown("---")

# Chart 3: TCAC Resource Levels
# Check if TCAC data exists (all values are not zero)
has_tcac_data = any(any(data["tcac_values"]) for data in all_data)

if has_tcac_data:
    render_title("Units by TCAC resource level", is_embedded)
    tcac_levels = ["Not TCAC", "Low", "Moderate", "High", "Highest"]

    fig_tcac = create_multi_scenario_stacked_chart(
        all_data, tcac_levels, "tcac_values", tcac_colors
    )
    st.plotly_chart(fig_tcac, width="stretch")
    render_subheader("TCAC Data", is_embedded)
    tcac_data_values = {level: [] for level in tcac_levels}
    for data in all_data:
        for i, level in enumerate(tcac_levels):
            tcac_data_values[level].append(data["tcac_values"][i])
    df_tcac = pd.DataFrame(tcac_data_values, index=scenario_names)
    st.dataframe(df_tcac.T, width="stretch")

    st.markdown("---")

# Chart 4: Fire Hazard Severity Zone (FHSZ)
# Check if fire risk data exists (has fire_risk_values in all scenarios)
has_fire_data = all(
    "fire_risk_values" in data and data["fire_risk_values"] for data in all_data
)

if has_fire_data:
    render_title("Units by Fire Risk", is_embedded)
    fire_risk_levels = ["None", "High", "Very High"]
    fire_risk_data_values = {level: [] for level in fire_risk_levels}
    fire_risk_data_pct = {level: [] for level in fire_risk_levels}
    for data in all_data:
        for i, level in enumerate(fire_risk_levels):
            fire_risk_data_values[level].append(data["fire_risk_values"][i])
            fire_risk_data_pct[level].append(data["fire_risk_pct"][i])

    df_fire_risk = pd.DataFrame(fire_risk_data_values, index=scenario_names)
    fig_fire_risk = create_multi_scenario_stacked_chart(
        all_data, fire_risk_levels, "fire_risk_values", fire_risk_colors
    )
    st.plotly_chart(fig_fire_risk, width="stretch")
    render_subheader("Fire Risk Data", is_embedded)
    st.dataframe(df_fire_risk.T, width="stretch")

    st.markdown("---")

# Summary of new development
render_title("Summary of new development", is_embedded)

# Chart 5: Units by Building Type
render_title("New development by building type", is_embedded)
unit_types_lowercase = ["sf", "th", "plex", "mf"]
unit_types_display = ["SF", "TH", "PLEX", "MF"]

# Create a mapping from display labels to colors using lowercase keys
unit_type_colors_display = {
    display: unit_type_colors[lower]
    for display, lower in zip(unit_types_display, unit_types_lowercase)
}

fig_unit_types = create_multi_scenario_stacked_chart(
    all_data, unit_types_display, "unit_type_values", unit_type_colors_display
)
st.plotly_chart(fig_unit_types, width="stretch")
render_subheader("Unit Type Data", is_embedded)
unit_type_data_values = {utype: [] for utype in unit_types_display}
for data in all_data:
    for i, utype in enumerate(unit_types_display):
        unit_type_data_values[utype].append(data["unit_type_values"][i])
df_unit_types = pd.DataFrame(unit_type_data_values, index=scenario_names)
st.dataframe(df_unit_types.T, width="stretch")

st.markdown("---")

# Chart 6: Income Brackets
render_title("New development by income affordability", is_embedded)
income_brackets = [
    "Market rate 0-50% MFI",
    "Market rate 50-100% MFI",
    "Market rate 100-150% MFI",
    "Market rate 150-200% MFI",
    "Market rate 200-250% MFI",
    "Market rate 250%+ MFI",
    "Affordable 0-50% AMI",
    "Affordable 50-80% AMI",
    "Affordable 80-100% AMI",
    "Affordable 100-120% AMI",
    "Affordable 120%+ AMI",
]

fig_income = create_multi_scenario_stacked_chart(
    all_data, income_brackets, "income_values", income_bracket_colors
)
st.plotly_chart(fig_income, width="stretch")
render_subheader("Income Bracket Data", is_embedded)
income_data_values = {bracket: [] for bracket in income_brackets}
for data in all_data:
    for i, bracket in enumerate(income_brackets):
        income_data_values[bracket].append(data["income_values"][i])
df_income = pd.DataFrame(income_data_values, index=scenario_names)
st.dataframe(df_income.T, width="stretch")

st.markdown("---")

# Chart 7: Bedroom Counts
render_title("New development by bedroom count", is_embedded)
bedroom_counts = [
    "0 bedrooms",
    "1 bedroom",
    "2 bedrooms",
    "3+ bedrooms",
    "Affordable 0 bedrooms",
    "Affordable 1 bedroom",
    "Affordable 2 bedrooms",
    "Affordable 3+ bedrooms",
]

fig_bedrooms = create_multi_scenario_stacked_chart(
    all_data, bedroom_counts, "bedroom_values", bedroom_count_colors
)
st.plotly_chart(fig_bedrooms, width="stretch")
render_subheader("Bedroom Count Data", is_embedded)
bedroom_data_values = {count: [] for count in bedroom_counts}
for data in all_data:
    for i, count in enumerate(bedroom_counts):
        bedroom_data_values[count].append(data["bedroom_values"][i])
df_bedrooms = pd.DataFrame(bedroom_data_values, index=scenario_names)
st.dataframe(df_bedrooms.T, width="stretch")

st.markdown("---")

# Chart 8: Parking Types
render_title("New parking stalls by type", is_embedded)
parking_types = ["Surface", "Garage", "Podium", "Structured", "Underground"]

fig_parking = create_multi_scenario_stacked_chart(
    all_data, parking_types, "parking_values", parking_type_colors
)
st.plotly_chart(fig_parking, width="stretch")
render_subheader("Parking Data", is_embedded)
parking_data_values = {ptype: [] for ptype in parking_types}
for data in all_data:
    for i, ptype in enumerate(parking_types):
        parking_data_values[ptype].append(data["parking_values"][i])
df_parking = pd.DataFrame(parking_data_values, index=scenario_names)
st.dataframe(df_parking.T, width="stretch")

st.markdown("---")

# Land Area Coverage by Density and FAR
render_title("Land Area Coverage", is_embedded)

density_labels = ["<10 DUA", "11-25 DUA", "26-50 DUA", "51-75 DUA", ">75 DUA"]
far_labels = ["<0.2 FAR", "0.2-0.6 FAR", "0.6-1 FAR", "1-2 FAR", "2-4 FAR", ">4 FAR"]

# Chart: Land Area Coverage by Density
render_title("Land area cover by DUA (acres)", is_embedded)
fig_density = create_multi_scenario_stacked_chart(
    all_data, density_labels, "density_values", density_colors
)
st.plotly_chart(fig_density, width="stretch")
render_subheader("DUA Data", is_embedded)
density_data_values = {label: [] for label in density_labels}
for data in all_data:
    for i, label in enumerate(density_labels):
        density_data_values[label].append(data["density_values"][i])
df_density = pd.DataFrame(density_data_values, index=scenario_names)
st.dataframe(df_density.T, width="stretch")

st.markdown("---")

# Chart: Land Area Coverage by FAR (Bulk)
render_title("Land area cover by FAR (acres)", is_embedded)
fig_far = create_multi_scenario_stacked_chart(
    all_data, far_labels, "far_values", far_colors
)
st.plotly_chart(fig_far, width="stretch")
render_subheader("FAR Data", is_embedded)
far_data_values = {label: [] for label in far_labels}
for data in all_data:
    for i, label in enumerate(far_labels):
        far_data_values[label].append(data["far_values"][i])
df_far = pd.DataFrame(far_data_values, index=scenario_names)
st.dataframe(df_far.T, width="stretch")
