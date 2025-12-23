import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from urllib.parse import unquote

# ============================================================================
# Data Loading Functions
# ============================================================================


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

# Check for CSV URL parameters
params = st.query_params

urls = {
    "apply_zoning": "https://storage.googleapis.com/mapcraftlabs.appspot.com/labs_data/StandardCalifornia/simulations/-Ogiwnj-fYy4wjWPOn8-/aggregations/full_aggregations.csv?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=mapcraftlabs%40appspot.gserviceaccount.com%2F20251218%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20251218T005811Z&X-Goog-Expires=604800&X-Goog-SignedHeaders=host&X-Goog-Signature=68e7acd3073a81f00b6ec564a7502d59032f314d0bd625fb14a38a57841b77e335ba02b5147e43f7b8f780a0451ce4262542f2d15f4a3cbb5add7386d7acad792ec7f206c5ae612b845c893bb78411436e2745a3553c27e55aba7554fcd1665c0041ac57c1728816523fe4d64c35a6648b4c8149286d17b568305013ea312e61bb37c7f9fb2fff08ab42ddeae36d8ae1c0203d827210e7450a7bd3b9188dd65711ad602eab57c9e0b79587eaa22ee0aa6ff3d8631fb5f6e4ef0d9c6f09bfb9563e6a7d7fccac08dc41e6e99633a871839cd7b45ef1cc0390ece3eb970c100cefde51bcd863ba4914e223aabf02cb1b4417ff71fc4a07623a7c92549879fc5861",
    "ignore_zoning": "https://storage.googleapis.com/mapcraftlabs.appspot.com/labs_data/StandardCalifornia/simulations/-Ogiwo-hmQWX6i7THCN2/aggregations/full_aggregations.csv?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=mapcraftlabs%40appspot.gserviceaccount.com%2F20251218%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20251218T005811Z&X-Goog-Expires=604800&X-Goog-SignedHeaders=host&X-Goog-Signature=6eef358214e5942bb2ca35e415234e70d9f84d7f3a0dc3be28e9525f6ce11f8408b17371795bd60735be1b9b275a77855b4edffd463190ad1274f9561980be76af340efa133e3532e5549420bed28c854b2c2f3cef3aa06d10f6d724dd125e2e8e5892b897d9b697519fd77f1cb2448ce2868e2ea001ed4806b915963788f1dfdba722f793ee2316d5f5b5255a1ae0f12c8f39b261a58d3fca15fd88f4d573b9d85e01ffc0d91860dc36efe12a17f1c40e5ee2291fe3ce7fe3a387871e319b61b3f15bf8a2fbecafd4d36a35f563bc995a570e69c42cac8941501086ac2c266095f19a837e2b5f0af3f58035e4ed50760229b8cb8cae75ff2e21c1d41672590b",
}

default_unzoned_url = urls["ignore_zoning"]
default_zoned_url = urls["apply_zoning"]

# Load unzoned baseline
unzoned_csv_url = (
    unquote(params.get("unzoned_url"))
    if params.get("unzoned_url")
    else default_unzoned_url
)

# Load multiple zoned scenarios
zoned_scenarios = []
for i in range(1, 10):  # Support up to 9 scenarios
    url_key = f"zoned_url_{i}"
    url = params.get(url_key)
    if url:
        url = unquote(url)
    elif not url and i < 3:
        url = default_zoned_url
    if url:
        zoned_scenarios.append({"url": url, "name": f"Scenario {i}"})

# Validate we have at least one URL
if not unzoned_csv_url and not zoned_scenarios:
    st.error(
        "Data not found. Please provide 'unzoned_url' and/or 'zoned_url' query parameters."
    )
    st.info(
        "Example: ?unzoned_url=https://example.com/unzoned.csv&zoned_url_1=https://example.com/zoned1.csv&zoned_url_2=https://example.com/zoned2.csv"
    )
    st.stop()

# Load all data
all_data = []

# Load unzoned baseline first (will be leftmost in charts)
if unzoned_csv_url:
    unzoned_data = load_data_from_aggregation_csv(unzoned_csv_url, "Unzoned")
    if unzoned_data:
        all_data.append(unzoned_data)

# Load all zoned scenarios
for scenario in zoned_scenarios:
    scenario_data = load_data_from_aggregation_csv(scenario["url"], scenario["name"])
    if scenario_data:
        all_data.append(scenario_data)

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
for data in all_data:
    scenario_names.append(data["scenario_name"])
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
