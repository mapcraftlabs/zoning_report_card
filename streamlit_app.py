"""
Market-Feasible Units Dashboard - Main Streamlit Application
"""

import streamlit as st
import pandas as pd
from datetime import datetime

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


# ============================================================================
# Main Dashboard
# ============================================================================

st.set_page_config(page_title="Market-Feasible Units Dashboard", layout="wide")

try:
    # Check for simulation ID parameters
    params = st.query_params

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
st.title("Market-Feasible Units Dashboard")

if all_metadata:
    st.subheader("Simulation Details")

    # Format the metadata for display
    metadata_display = []
    for meta in all_metadata:
        # Format the date nicely
        create_date = meta["createDate"]
        if create_date:
            try:
                dt = datetime.fromisoformat(create_date.replace("Z", "+00:00"))
                formatted_date = dt.strftime("%B %d, %Y at %I:%M %p")
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
st.title("Feasibility Summary")
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
st.subheader("Feasibility Data")
st.dataframe(df_total.T, width="stretch")

st.markdown("---")

# Chart 2: Units by Location
st.title("Units by Location")

location_configs = [
    ("fault_zone", "Fault Zone", "#D66E6C"),
    ("historic_district", "Historic District", "#6B9BD1"),
    ("urbanized", "Urbanized", "#6FB573"),
    ("walkable", "Walkable", "#F4C04E"),
    ("near_transit", "Near Transit", "#5DBDB4"),
    ("wui", "WUI", "#F07D4A"),
]

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

df_location_with_total = pd.DataFrame(location_data_with_total, index=scenario_names)
st.subheader("Location Data")
st.dataframe(df_location_with_total.T, width="stretch")

st.markdown("---")

# Chart 3: TCAC Resource Levels
st.title("Total units by TCAC resource level")
tcac_levels = ["Low", "Moderate", "High", "Highest"]

fig_tcac = create_multi_scenario_stacked_chart(
    all_data, tcac_levels, "tcac_values", tcac_colors
)
st.plotly_chart(fig_tcac, width="stretch")
st.subheader("TCAC Data")
tcac_data_values = {level: [] for level in tcac_levels}
for data in all_data:
    for i, level in enumerate(tcac_levels):
        tcac_data_values[level].append(data["tcac_values"][i])
df_tcac = pd.DataFrame(tcac_data_values, index=scenario_names)
st.dataframe(df_tcac.T, width="stretch")

st.markdown("---")

# Chart 4: Fire Hazard Severity Zone (FHSZ)
st.title("Units by Fire Risk")
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
st.subheader("Fire Risk Data")
st.dataframe(df_fire_risk.T, width="stretch")

st.markdown("---")

# Chart 5: Income Brackets
st.title("New development by income affordability")
income_brackets = [
    "<=50% MFI",
    "51%-100% MFI",
    "101-150% MFI",
    "151-200% MFI",
    "201-250% MFI",
    ">251% MFI",
]

fig_income = create_multi_scenario_stacked_chart(
    all_data, income_brackets, "income_values", income_bracket_colors
)
st.plotly_chart(fig_income, width="stretch")
st.subheader("Income Bracket Data")
income_data_values = {bracket: [] for bracket in income_brackets}
for data in all_data:
    for i, bracket in enumerate(income_brackets):
        income_data_values[bracket].append(data["income_values"][i])
df_income = pd.DataFrame(income_data_values, index=scenario_names)
st.dataframe(df_income.T, width="stretch")

st.markdown("---")

# Chart 6: Units by Building Type
st.title("New development by building type")
unit_types = ["SF", "TH", "PLEX", "MF"]

fig_unit_types = create_multi_scenario_stacked_chart(
    all_data, unit_types, "unit_type_values", unit_type_colors
)
st.plotly_chart(fig_unit_types, width="stretch")
st.subheader("Unit Type Data")
unit_type_data_values = {utype: [] for utype in unit_types}
for data in all_data:
    for i, utype in enumerate(unit_types):
        unit_type_data_values[utype].append(data["unit_type_values"][i])
df_unit_types = pd.DataFrame(unit_type_data_values, index=scenario_names)
st.dataframe(df_unit_types.T, width="stretch")

st.markdown("---")

# Chart 7: Bedroom Counts
st.title("New development by bedroom count")
bedroom_counts = ["0 bedrooms", "1 bedroom", "2 bedrooms", "3+ bedrooms"]

fig_bedrooms = create_multi_scenario_stacked_chart(
    all_data, bedroom_counts, "bedroom_values", bedroom_count_colors
)
st.plotly_chart(fig_bedrooms, width="stretch")
st.subheader("Bedroom Count Data")
bedroom_data_values = {count: [] for count in bedroom_counts}
for data in all_data:
    for i, count in enumerate(bedroom_counts):
        bedroom_data_values[count].append(data["bedroom_values"][i])
df_bedrooms = pd.DataFrame(bedroom_data_values, index=scenario_names)
st.dataframe(df_bedrooms.T, width="stretch")

st.markdown("---")

# Chart 8: Parking Types
st.title("New parking stalls by type")
parking_types = ["Surface", "Garage", "Podium", "Structured", "Underground"]

fig_parking = create_multi_scenario_stacked_chart(
    all_data, parking_types, "parking_values", parking_type_colors
)
st.plotly_chart(fig_parking, width="stretch")
st.subheader("Parking Data")
parking_data_values = {ptype: [] for ptype in parking_types}
for data in all_data:
    for i, ptype in enumerate(parking_types):
        parking_data_values[ptype].append(data["parking_values"][i])
df_parking = pd.DataFrame(parking_data_values, index=scenario_names)
st.dataframe(df_parking.T, width="stretch")

st.markdown("---")

# Land Area Coverage by Density and FAR
st.title("Land Area Coverage")

density_labels = ["<10 DUA", "11-25 DUA", "26-50 DUA", "51-75 DUA", ">75 DUA"]
far_labels = ["<0.2 FAR", "0.2-0.6 FAR", "0.6-1 FAR", "1-2 FAR", "2-4 FAR", ">4 FAR"]

# Chart: Land Area Coverage by Density
st.title("Land area cover by DUA (acres)")
fig_density = create_multi_scenario_stacked_chart(
    all_data, density_labels, "density_values", density_colors
)
st.plotly_chart(fig_density, width="stretch")
st.subheader("DUA Data")
density_data_values = {label: [] for label in density_labels}
for data in all_data:
    for i, label in enumerate(density_labels):
        density_data_values[label].append(data["density_values"][i])
df_density = pd.DataFrame(density_data_values, index=scenario_names)
st.dataframe(df_density.T, width="stretch")

st.markdown("---")

# Chart: Land Area Coverage by FAR (Bulk)
st.title("Land area cover by FAR (acres)")
fig_far = create_multi_scenario_stacked_chart(
    all_data, far_labels, "far_values", far_colors
)
st.plotly_chart(fig_far, width="stretch")
st.subheader("FAR Data")
far_data_values = {label: [] for label in far_labels}
for data in all_data:
    for i, label in enumerate(far_labels):
        far_data_values[label].append(data["far_values"][i])
df_far = pd.DataFrame(far_data_values, index=scenario_names)
st.dataframe(df_far.T, width="stretch")
