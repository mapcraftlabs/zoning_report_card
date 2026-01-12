import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from urllib.parse import unquote
import requests
import io

# ============================================================================
# Data Loading Functions
# ============================================================================


def fetch_data_from_api(simulation_ids, project_id):
    """
    Fetch aggregation data from the MapCraft API for multiple simulation IDs.

    Args:
        simulation_ids: List of simulation IDs to fetch
        project_id: The project ID to fetch data for

    Returns:
        Dictionary containing the CSV data or None if error
    """
    try:
        url = f"https://api.mapcraft.io/simulations/full_aggregations/{project_id}"
        response = requests.post(
            url, json={"simulation_ids": simulation_ids}, timeout=30
        )

        if response.status_code != 200:
            st.error(
                f"API request failed with status {response.status_code}: {response.text}"
            )
            return None

        return response.json()

    except Exception as e:
        st.error(f"Error fetching data from API: {e}")
        import traceback

        st.error(traceback.format_exc())
        return None


def load_data_from_aggregation_csv(url, scenario_name):
    """
    Load data from a single aggregation CSV file.

    Expected CSV format from Firebase:
    - marketUnits050Sum: <=50% MFI units
    - marketUnits51100Sum: 51%-100% MFI units
    - marketUnits101150Sum: 101-150% MFI units
    - marketUnits151200Sum: 151-200% MFI units
    - marketUnits201250Sum: 201-250% MFI units
    - marketUnits251Sum: >251% MFI units
    - countMarket0BrSum: 0 bedroom units
    - countMarket1BrSum: 1 bedroom units
    - countMarket2BrSum: 2 bedroom units
    - countMarket3BrSum: 3+ bedroom units
    - totalUnitsSum: total units
    - affordableUnitsSum: affordable units
    - surfaceParkingStallsSum, garageParkingStallsSum, etc.
    """
    try:
        if not url:
            return None

        df = pd.read_csv(url)

        # Helper to get first row value or 0
        def get_value(column):
            if column in df.columns and len(df) > 0:
                return df[column].iloc[0]
            return 0

        # Extract income bracket data
        income_values = [
            get_value("marketUnits050Sum"),
            get_value("marketUnits51100Sum"),
            get_value("marketUnits101150Sum"),
            get_value("marketUnits151200Sum"),
            get_value("marketUnits201250Sum"),
            get_value("marketUnits251Sum"),
        ]

        total_income = sum(income_values)
        income_pct = [
            round(v / total_income * 100) if total_income > 0 else 0
            for v in income_values
        ]

        # Extract bedroom count data
        bedroom_values = [
            get_value("countMarket0BrSum"),
            get_value("countMarket1BrSum"),
            get_value("countMarket2BrSum"),
            get_value("countMarket3BrSum"),
        ]

        total_bedroom = sum(bedroom_values)
        bedroom_pct = [
            round(v / total_bedroom * 100) if total_bedroom > 0 else 0
            for v in bedroom_values
        ]

        # Extract parking data
        parking_values = [
            get_value("surfaceParkingStallsSum"),
            get_value("garageParkingStallsSum"),
            get_value("podiumParkingStallsSum"),
            get_value("structuredParkingStallsSum"),
            get_value("undergroundParkingStallsSum"),
        ]

        total_parking = sum(parking_values)
        parking_pct = [
            round(v / total_parking * 100) if total_parking > 0 else 0
            for v in parking_values
        ]

        # Extract density (DUA) data - land area by density ranges (in acres)
        density_values = [
            get_value("acresDuaLt10Sum"),  # <10 DUA
            get_value("acresDua1025Sum"),  # 11-25 DUA (actually 10-25 in data)
            get_value("acresDua2550Sum"),  # 26-50 DUA (actually 25-50 in data)
            get_value("acresDua5075Sum"),  # 51-75 DUA (actually 50-75 in data)
            get_value("acresDuaGt75Sum"),  # >75 DUA
        ]

        total_density_area = sum(density_values)
        density_pct = [
            round(v / total_density_area * 100, 1) if total_density_area > 0 else 0
            for v in density_values
        ]

        # Extract FAR (bulk) data - land area by FAR ranges (in acres)
        far_values = [
            get_value("acresFarLtpt2Sum"),  # <0.2 FAR (display as <0.4)
            get_value("acresFarPt2Pt6Sum"),  # 0.2-0.6 FAR (display as 0.4-0.6)
            get_value("acresFarPt61Sum"),  # 0.6-1 FAR (display as 0.7-0.9)
            get_value("acresFar12Sum"),  # 1-2 FAR (display as 1-4)
            get_value("acresFar24Sum"),  # 2-4 FAR (display as 5-7)
            get_value("acresFarGt4Sum"),  # >4 FAR (display as 8+)
        ]

        total_far_area = sum(far_values)
        far_pct = [
            round(v / total_far_area * 100, 1) if total_far_area > 0 else 0
            for v in far_values
        ]

        # Extract units by type data
        unit_type_values = [
            get_value("unitsByTypeSFSum"),  # SF
            get_value("unitsByTypeTHSum"),  # TH
            get_value("unitsByTypePLEXSum"),  # PLEX
            get_value("unitsByTypeMFSum"),  # MF
        ]

        total_unit_types = sum(unit_type_values)
        unit_type_pct = [
            round(v / total_unit_types * 100, 1) if total_unit_types > 0 else 0
            for v in unit_type_values
        ]

        # Extract TCAC resource level data
        tcac_values = [
            get_value("unitsByTcacLowResourceSum"),  # Low
            get_value("unitsByTcacModerateResourceSum"),  # Moderate
            get_value("unitsByTcacHighResourceSum"),  # High
            get_value("unitsByTcacHighestResourceSum"),  # Highest
        ]

        total_tcac = sum(tcac_values)
        tcac_pct = [
            round(v / total_tcac * 100, 1) if total_tcac > 0 else 0 for v in tcac_values
        ]

        # Extract location-based data
        location_data = {
            "fault_zone": get_value("unitsFaultZoneSum"),
            "historic_district": get_value("unitsHistoricDistrictSum"),
            "urbanized": get_value("unitsUrbanizedSum"),
            "walkable": get_value("unitsWalkableSum"),
            "near_transit": get_value("unitsNearTransitSum"),
            "wui": get_value("unitsWuiSum"),
        }

        # Get totals
        total_units = get_value("totalUnitsSum")
        affordable_units = get_value("affordableUnitsSum")

        # Extract fire hazard severity zone (FHSZ) data
        fhsz_high = get_value("unitsFhszHighSum")
        fhsz_very_high = get_value("unitsFhszVeryhighSum")
        fhsz_no = total_units - fhsz_high - fhsz_very_high

        fire_risk_values = [
            fhsz_no,  # No fire risk
            fhsz_high,  # High
            fhsz_very_high,  # Very High
        ]

        total_fire_risk = sum(fire_risk_values)
        fire_risk_pct = [
            round(v / total_fire_risk * 100, 1) if total_fire_risk > 0 else 0
            for v in fire_risk_values
        ]

        return {
            "scenario_name": scenario_name,
            "income_values": [round(v, 1) for v in income_values],
            "income_pct": income_pct,
            "bedroom_values": [round(v, 1) for v in bedroom_values],
            "bedroom_pct": bedroom_pct,
            "parking_values": [round(v, 1) for v in parking_values],
            "parking_pct": parking_pct,
            "density_values": [round(v, 1) for v in density_values],
            "density_pct": density_pct,
            "far_values": [round(v, 1) for v in far_values],
            "far_pct": far_pct,
            "unit_type_values": [round(v, 1) for v in unit_type_values],
            "unit_type_pct": unit_type_pct,
            "tcac_values": [round(v, 1) for v in tcac_values],
            "tcac_pct": tcac_pct,
            "fire_risk_values": [round(v, 1) for v in fire_risk_values],
            "fire_risk_pct": fire_risk_pct,
            "location_data": location_data,
            "total_units": total_units,
            "affordable_units": affordable_units,
        }

    except Exception as e:
        st.error(f"Error loading CSV data from {url}: {e}")
        import traceback

        st.error(traceback.format_exc())
        return None


def process_aggregation_data(data_dict, scenario_name):
    """
    Process aggregation data from API response dict.

    Args:
        data_dict: Dictionary containing aggregation data
        scenario_name: Name for this scenario

    Returns:
        Processed data dictionary with percentages and organized values
    """
    try:
        # Helper to get value or 0
        def get_value(key):
            return data_dict.get(key, 0)

        # Extract income bracket data
        income_values = [
            get_value("marketUnits050Sum"),
            get_value("marketUnits51100Sum"),
            get_value("marketUnits101150Sum"),
            get_value("marketUnits151200Sum"),
            get_value("marketUnits201250Sum"),
            get_value("marketUnits251Sum"),
        ]

        total_income = sum(income_values)
        income_pct = [
            round(v / total_income * 100) if total_income > 0 else 0
            for v in income_values
        ]

        # Extract bedroom count data
        bedroom_values = [
            get_value("countMarket0BrSum"),
            get_value("countMarket1BrSum"),
            get_value("countMarket2BrSum"),
            get_value("countMarket3BrSum"),
        ]

        total_bedroom = sum(bedroom_values)
        bedroom_pct = [
            round(v / total_bedroom * 100) if total_bedroom > 0 else 0
            for v in bedroom_values
        ]

        # Extract parking data
        parking_values = [
            get_value("surfaceParkingStallsSum"),
            get_value("garageParkingStallsSum"),
            get_value("podiumParkingStallsSum"),
            get_value("structuredParkingStallsSum"),
            get_value("undergroundParkingStallsSum"),
        ]

        total_parking = sum(parking_values)
        parking_pct = [
            round(v / total_parking * 100) if total_parking > 0 else 0
            for v in parking_values
        ]

        # Extract density (DUA) data - land area by density ranges (in acres)
        density_values = [
            get_value("acresDuaLt10Sum"),  # <10 DUA
            get_value("acresDua1025Sum"),  # 11-25 DUA (actually 10-25 in data)
            get_value("acresDua2550Sum"),  # 26-50 DUA (actually 25-50 in data)
            get_value("acresDua5075Sum"),  # 51-75 DUA (actually 50-75 in data)
            get_value("acresDuaGt75Sum"),  # >75 DUA
        ]

        total_density_area = sum(density_values)
        density_pct = [
            round(v / total_density_area * 100, 1) if total_density_area > 0 else 0
            for v in density_values
        ]

        # Extract FAR (bulk) data - land area by FAR ranges (in acres)
        far_values = [
            get_value("acresFarLtpt2Sum"),  # <0.2 FAR (display as <0.4)
            get_value("acresFarPt2Pt6Sum"),  # 0.2-0.6 FAR (display as 0.4-0.6)
            get_value("acresFarPt61Sum"),  # 0.6-1 FAR (display as 0.7-0.9)
            get_value("acresFar12Sum"),  # 1-2 FAR (display as 1-4)
            get_value("acresFar24Sum"),  # 2-4 FAR (display as 5-7)
            get_value("acresFarGt4Sum"),  # >4 FAR (display as 8+)
        ]

        total_far_area = sum(far_values)
        far_pct = [
            round(v / total_far_area * 100, 1) if total_far_area > 0 else 0
            for v in far_values
        ]

        # Extract units by type data
        unit_type_values = [
            get_value("unitsByTypeSFSum"),  # SF
            get_value("unitsByTypeTHSum"),  # TH
            get_value("unitsByTypePLEXSum"),  # PLEX
            get_value("unitsByTypeMFSum"),  # MF
        ]

        total_unit_types = sum(unit_type_values)
        unit_type_pct = [
            round(v / total_unit_types * 100, 1) if total_unit_types > 0 else 0
            for v in unit_type_values
        ]

        # Extract TCAC resource level data
        tcac_values = [
            get_value("unitsByTcacLowResourceSum"),  # Low
            get_value("unitsByTcacModerateResourceSum"),  # Moderate
            get_value("unitsByTcacHighResourceSum"),  # High
            get_value("unitsByTcacHighestResourceSum"),  # Highest
        ]

        total_tcac = sum(tcac_values)
        tcac_pct = [
            round(v / total_tcac * 100, 1) if total_tcac > 0 else 0 for v in tcac_values
        ]

        # Extract location-based data
        location_data = {
            "fault_zone": get_value("unitsFaultZoneSum"),
            "historic_district": get_value("unitsHistoricDistrictSum"),
            "urbanized": get_value("unitsUrbanizedSum"),
            "walkable": get_value("unitsWalkableSum"),
            "near_transit": get_value("unitsNearTransitSum"),
            "wui": get_value("unitsWuiSum"),
        }

        # Get totals
        total_units = get_value("totalUnitsSum")
        affordable_units = get_value("affordableUnitsSum")

        # Extract fire hazard severity zone (FHSZ) data
        fhsz_high = get_value("unitsFhszHighSum")
        fhsz_very_high = get_value("unitsFhszVeryhighSum")
        fhsz_no = total_units - fhsz_high - fhsz_very_high

        fire_risk_values = [
            fhsz_no,  # No fire risk
            fhsz_high,  # High
            fhsz_very_high,  # Very High
        ]

        total_fire_risk = sum(fire_risk_values)
        fire_risk_pct = [
            round(v / total_fire_risk * 100, 1) if total_fire_risk > 0 else 0
            for v in fire_risk_values
        ]

        return {
            "scenario_name": scenario_name,
            "income_values": [round(v, 1) for v in income_values],
            "income_pct": income_pct,
            "bedroom_values": [round(v, 1) for v in bedroom_values],
            "bedroom_pct": bedroom_pct,
            "parking_values": [round(v, 1) for v in parking_values],
            "parking_pct": parking_pct,
            "density_values": [round(v, 1) for v in density_values],
            "density_pct": density_pct,
            "far_values": [round(v, 1) for v in far_values],
            "far_pct": far_pct,
            "unit_type_values": [round(v, 1) for v in unit_type_values],
            "unit_type_pct": unit_type_pct,
            "tcac_values": [round(v, 1) for v in tcac_values],
            "tcac_pct": tcac_pct,
            "fire_risk_values": [round(v, 1) for v in fire_risk_values],
            "fire_risk_pct": fire_risk_pct,
            "location_data": location_data,
            "total_units": total_units,
            "affordable_units": affordable_units,
        }

    except Exception as e:
        st.error(f"Error processing aggregation data: {e}")
        import traceback

        st.error(traceback.format_exc())
        return None


# Color schemes
total_feasibility_color = "#D66E6C"
building_type_colors = {
    "Single": "#6B9BD1",
    "Single w/ ADU": "#5DBDB4",
    "Townhomes": "#F07D4A",
    "Plexes": "#6FB573",
    "Walkups": "#F4C04E",
    "Podiums": "#D66E6C",
    "Towers": "#5A7BC4",
}

income_bracket_colors = {
    "<=50% MFI": "#5DBDB4",
    "51%-100% MFI": "#F07D4A",
    "101-150% MFI": "#6FB573",
    "151-200% MFI": "#F4C04E",
    "201-250% MFI": "#D66E6C",
    ">251% MFI": "#6B9BD1",
}

bedroom_count_colors = {
    "0 bedrooms": "#6FB573",
    "1 bedroom": "#F4C04E",
    "2 bedrooms": "#D66E6C",
    "3+ bedrooms": "#6B9BD1",
}

parking_type_colors = {
    "Surface": "#6FB573",
    "Garage": "#F4C04E",
    "Podium": "#D66E6C",
    "Structured": "#6B9BD1",
    "Underground": "#5DBDB4",
}

density_colors = {
    "<10 DUA": "#F07D4A",
    "11-25 DUA": "#6FB573",
    "26-50 DUA": "#F4C04E",
    "51-75 DUA": "#D66E6C",
    ">75 DUA": "#6B9BD1",
}

far_colors = {
    "<0.2 FAR": "#5DBDB4",
    "0.2-0.6 FAR": "#F07D4A",
    "0.6-1 FAR": "#6FB573",
    "1-2 FAR": "#F4C04E",
    "2-4 FAR": "#D66E6C",
    ">4 FAR": "#6B9BD1",
}

unit_type_colors = {
    "SF": "#6B9BD1",
    "MF": "#F07D4A",
    "TH": "#6FB573",
    "PLEX": "#F4C04E",
}

tcac_colors = {
    "Low": "#D66E6C",
    "Moderate": "#F4C04E",
    "High": "#6FB573",
    "Highest": "#6B9BD1",
}

fire_risk_colors = {
    "None": "#6FB573",
    "High": "#F4C04E",
    "Very High": "#D66E6C",
}

# ============================================================================
# Chart Functions
# ============================================================================


def create_multi_scenario_stacked_chart(all_data, categories, data_key, colors):
    """Create stacked bar chart with multiple scenarios."""
    fig = go.Figure()

    # Get scenario names
    scenario_names = [d["scenario_name"] for d in all_data]

    # Add bars for each category in normal order
    for i in range(len(categories)):
        category = categories[i]
        # Get values for this category across all scenarios
        if data_key == "income_values":
            values = [d["income_values"][i] for d in all_data]
        elif data_key == "bedroom_values":
            values = [d["bedroom_values"][i] for d in all_data]
        elif data_key == "parking_values":
            values = [d["parking_values"][i] for d in all_data]
        elif data_key == "density_values":
            values = [d["density_values"][i] for d in all_data]
        elif data_key == "far_values":
            values = [d["far_values"][i] for d in all_data]
        elif data_key == "unit_type_values":
            values = [d["unit_type_values"][i] for d in all_data]
        elif data_key == "tcac_values":
            values = [d["tcac_values"][i] for d in all_data]
        elif data_key == "fire_risk_values":
            values = [d["fire_risk_values"][i] for d in all_data]

        fig.add_trace(
            go.Bar(
                name=category,
                x=scenario_names,
                y=values,
                marker_color=colors[category],
                text=[f"{int(v)}" if v > 0 else "" for v in values],
                textposition="inside",
                textfont=dict(color="white", size=14),
                hovertemplate=f"{category}: %{{y}}<extra></extra>",
            )
        )

    # Update layout
    fig.update_layout(
        barmode="stack",
        height=600,
        xaxis=dict(title="", tickfont=dict(size=14)),
        yaxis=dict(
            title="", showticklabels=False, showgrid=True, gridcolor="lightgray"
        ),
        legend=dict(
            title="",
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=-0.15,
            font=dict(size=12),
            traceorder="normal",
        ),
        plot_bgcolor="white",
        margin=dict(l=0, r=20, t=30, b=30),
    )

    return fig


def create_total_feasibility_chart_grouped(scenario_names, total_data_dict, color):
    """Create grouped bar chart for total units vs affordable units."""
    fig = go.Figure()

    # Add Total Units bar
    fig.add_trace(
        go.Bar(
            name="Total Units",
            x=scenario_names,
            y=total_data_dict["Total Units"],
            marker_color=color,
            text=[f"{int(v)}" for v in total_data_dict["Total Units"]],
            textposition="inside",
            textfont=dict(color="white", size=14, weight="bold"),
            hovertemplate="Total Units: %{y}<extra></extra>",
        )
    )

    # Add Affordable Units bar with minimum display value
    max_value = max(
        max(total_data_dict["Total Units"]), max(total_data_dict["Affordable Units"])
    )
    min_display_value = max_value * 0.01

    affordable_display = [
        val if val > 0 else min_display_value
        for val in total_data_dict["Affordable Units"]
    ]

    fig.add_trace(
        go.Bar(
            name="Affordable Units",
            x=scenario_names,
            y=affordable_display,
            marker_color="#5DBDB4",
            text=[
                f"{int(actual)}" if actual > 0 else ""
                for actual in total_data_dict["Affordable Units"]
            ],
            textposition="inside",
            textfont=dict(color="white", size=14, weight="bold"),
            hovertemplate="Affordable Units: %{customdata}<extra></extra>",
            customdata=total_data_dict["Affordable Units"],
        )
    )

    # Update layout
    fig.update_layout(
        barmode="group",
        height=400,
        xaxis=dict(title="", tickfont=dict(size=14)),
        yaxis=dict(
            title="",
            showgrid=True,
            gridcolor="lightgray",
            showticklabels=False,
        ),
        plot_bgcolor="white",
        margin=dict(l=0, r=20, t=30, b=30),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
    )

    return fig


def create_location_grouped_chart(all_data, location_configs, include_total=True):
    """Create grouped bar chart showing location-specific units across all scenarios."""
    fig = go.Figure()

    # Get scenario names
    scenario_names = [d["scenario_name"] for d in all_data]

    # Define colors for scenarios
    scenario_colors = ["#D66E6C", "#6B9BD1", "#6FB573", "#F4C04E", "#5DBDB4"]

    # Add bars for each scenario
    for idx, data in enumerate(all_data):
        if include_total:
            location_values = [data["total_units"]] + [
                data["location_data"][config[0]] for config in location_configs
            ]
            location_labels = ["Total Units"] + [
                config[1] for config in location_configs
            ]
        else:
            location_values = [
                data["location_data"][config[0]] for config in location_configs
            ]
            location_labels = [config[1] for config in location_configs]

        fig.add_trace(
            go.Bar(
                name=data["scenario_name"],
                x=location_labels,
                y=location_values,
                marker_color=scenario_colors[idx % len(scenario_colors)],
                text=[f"{int(v)}" if v > 0 else "" for v in location_values],
                textposition="inside",
                textfont=dict(color="white", size=14, weight="bold"),
                hovertemplate="%{x}: %{y}<extra></extra>",
            )
        )

    # Update layout
    fig.update_layout(
        barmode="group",
        height=500,
        xaxis=dict(title="", tickfont=dict(size=14)),
        yaxis=dict(
            title="",
            showgrid=True,
            gridcolor="lightgray",
            showticklabels=False,
        ),
        plot_bgcolor="white",
        margin=dict(l=0, r=20, t=30, b=30),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
    )

    return fig

    # Update layout
    fig.update_layout(
        height=400,
        xaxis=dict(title="", tickfont=dict(size=12), tickangle=-45),
        yaxis=dict(
            title="",
            showgrid=True,
            gridcolor="lightgray",
            showticklabels=False,
        ),
        plot_bgcolor="white",
        margin=dict(l=0, r=20, t=30, b=100),
        showlegend=False,
    )

    return fig


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
        st.info("**Please provide a project_id in the URL.**\n\n")
        st.stop()

    # Get simulation IDs from query params
    simulation_ids_param = params.get("simulation_ids")
    if not simulation_ids_param:
        st.error("❌ No simulation IDs provided")
        st.info("**Please provide simulation IDs in the URL.**\n\n")
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

# The API returns data as a dict with simulation IDs as keys
# Each value is a list with one element containing the aggregation data
for i, sim_id in enumerate(simulation_ids):
    if sim_id in api_response:
        # Get the list for this simulation ID and extract the first element
        data_list = api_response[sim_id]
        if data_list and len(data_list) > 0:
            raw_data = data_list[0]
            # Process the raw data into the expected format
            scenario_name = f"Scenario {i+1}"
            processed_data = process_aggregation_data(raw_data, scenario_name)
            if processed_data:
                all_data.append(processed_data)

# Check if we successfully loaded any data
if not all_data:
    st.error("Failed to load any data. Please check the URLs and try again.")
    st.stop()

# Define category labels
income_brackets = [
    "<=50% MFI",
    "51%-100% MFI",
    "101-150% MFI",
    "151-200% MFI",
    "201-250% MFI",
    ">251% MFI",
]
bedroom_counts = ["0 bedrooms", "1 bedroom", "2 bedrooms", "3+ bedrooms"]
parking_types = ["Surface", "Garage", "Podium", "Structured", "Underground"]

# Define category labels
income_brackets = [
    "<=50% MFI",
    "51%-100% MFI",
    "101-150% MFI",
    "151-200% MFI",
    "201-250% MFI",
    ">251% MFI",
]
bedroom_counts = ["0 bedrooms", "1 bedroom", "2 bedrooms", "3+ bedrooms"]
parking_types = ["Surface", "Garage", "Podium", "Structured", "Underground"]

# Chart 1: Total Feasibility
st.title("Market-Feasible Units Dashboard")
total_data_dict = {"Total Units": [], "Affordable Units": []}
scenario_names = []
for i, data in enumerate(all_data):
    # Set default scenario names if not provided in data
    scenario_name = data.get("scenario_name", f"Scenario {i+1}")
    scenario_names.append(scenario_name)
    total_data_dict["Total Units"].append(data["total_units"])
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
location_data_dict_full = {"Total Units": []}
for config in location_configs:
    location_data_dict_full[config[1]] = []

for data in all_data:
    location_data_dict_full["Total Units"].append(data["total_units"])
    for config in location_configs:
        location_data_dict_full[config[1]].append(data["location_data"][config[0]])

df_location = pd.DataFrame(location_data_dict_full, index=scenario_names)
st.subheader("Location Data")
st.dataframe(df_location.T, width="stretch")

st.markdown("---")

# Chart 3: Units by Type
st.title("Units by type")
unit_types = ["SF", "TH", "PLEX", "MF"]
unit_type_data_values = {utype: [] for utype in unit_types}
unit_type_data_pct = {utype: [] for utype in unit_types}
for data in all_data:
    for i, utype in enumerate(unit_types):
        unit_type_data_values[utype].append(data["unit_type_values"][i])
        unit_type_data_pct[utype].append(data["unit_type_pct"][i])

df_unit_types = pd.DataFrame(unit_type_data_values, index=scenario_names)
fig_unit_types = create_multi_scenario_stacked_chart(
    all_data, unit_types, "unit_type_values", unit_type_colors
)
st.plotly_chart(fig_unit_types, width="stretch")
st.subheader("Units by Type Data")
st.dataframe(df_unit_types.T, width="stretch")

st.markdown("---")

# Chart 3: TCAC Resource Levels
st.title("Units by TCAC resource level")
tcac_levels = ["Low", "Moderate", "High", "Highest"]
tcac_data_values = {level: [] for level in tcac_levels}
tcac_data_pct = {level: [] for level in tcac_levels}
for data in all_data:
    for i, level in enumerate(tcac_levels):
        tcac_data_values[level].append(data["tcac_values"][i])
        tcac_data_pct[level].append(data["tcac_pct"][i])

df_tcac = pd.DataFrame(tcac_data_values, index=scenario_names)
fig_tcac = create_multi_scenario_stacked_chart(
    all_data, tcac_levels, "tcac_values", tcac_colors
)
st.plotly_chart(fig_tcac, width="stretch")
st.subheader("TCAC Resource Level Data")
st.dataframe(df_tcac.T, width="stretch")

st.markdown("---")

# Chart 4: Income Brackets
st.title("Market-feasible units affordable to different income brackets")
income_data_values = {bracket: [] for bracket in income_brackets}
income_data_pct = {bracket: [] for bracket in income_brackets}
for data in all_data:
    for i, bracket in enumerate(income_brackets):
        income_data_values[bracket].append(data["income_values"][i])
        income_data_pct[bracket].append(data["income_pct"][i])

# Create dataframe for display (actual values)
df_income = pd.DataFrame(income_data_values, index=scenario_names)
fig_income = create_multi_scenario_stacked_chart(
    all_data, income_brackets, "income_values", income_bracket_colors
)
st.plotly_chart(fig_income, width="stretch")
st.subheader("Income Bracket Data")
st.dataframe(df_income.T, width="stretch")

st.markdown("---")

# Chart 4: Bedroom Counts
st.title("Market-feasible units by bedroom count")
bedroom_data_values = {count: [] for count in bedroom_counts}
bedroom_data_pct = {count: [] for count in bedroom_counts}
for data in all_data:
    for i, count in enumerate(bedroom_counts):
        bedroom_data_values[count].append(data["bedroom_values"][i])
        bedroom_data_pct[count].append(data["bedroom_pct"][i])

df_bedrooms = pd.DataFrame(bedroom_data_values, index=scenario_names)
fig_bedrooms = create_multi_scenario_stacked_chart(
    all_data, bedroom_counts, "bedroom_values", bedroom_count_colors
)
st.plotly_chart(fig_bedrooms, width="stretch")
st.subheader("Bedroom Count Data")
st.dataframe(df_bedrooms.T, width="stretch")

st.markdown("---")

# Chart 5: Parking Types
st.title("Parking stalls by type")
parking_data_values = {ptype: [] for ptype in parking_types}
parking_data_pct = {ptype: [] for ptype in parking_types}
for data in all_data:
    for i, ptype in enumerate(parking_types):
        parking_data_values[ptype].append(data["parking_values"][i])
        parking_data_pct[ptype].append(data["parking_pct"][i])

df_parking = pd.DataFrame(parking_data_values, index=scenario_names)
fig_parking = create_multi_scenario_stacked_chart(
    all_data, parking_types, "parking_values", parking_type_colors
)
st.plotly_chart(fig_parking, width="stretch")
st.subheader("Parking Data")
st.dataframe(df_parking.T, width="stretch")

st.markdown("---")

# Land Area Coverage by Density and FAR
st.title("Land Area Coverage")

density_labels = ["<10 DUA", "11-25 DUA", "26-50 DUA", "51-75 DUA", ">75 DUA"]
far_labels = ["<0.2 FAR", "0.2-0.6 FAR", "0.6-1 FAR", "1-2 FAR", "2-4 FAR", ">4 FAR"]

# Chart: Land Area Coverage by Density
st.title("Land area cover by density (acres)")
fig_density = create_multi_scenario_stacked_chart(
    all_data, density_labels, "density_values", density_colors
)
st.plotly_chart(fig_density, width="stretch")

st.markdown("---")

# Chart: Land Area Coverage by FAR (Bulk)
st.title("Land area cover by bulk (acres)")
fig_far = create_multi_scenario_stacked_chart(
    all_data, far_labels, "far_values", far_colors
)
st.plotly_chart(fig_far, width="stretch")

st.markdown("---")

# Chart: Fire Hazard Severity Zone (FHSZ)
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
