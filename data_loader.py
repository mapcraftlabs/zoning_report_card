"""
Data loading and processing functions for the zoning report card dashboard.
"""

import streamlit as st
import requests


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
        url = f"https://api.mapcraft.io/simulations/aggregations_data/{project_id}"
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
            get_value("affordableUnits30Sum"),
            get_value("affordableUnits50Sum"),
            get_value("affordableUnits60Sum"),
            get_value("affordableUnits80Sum"),
            get_value("affordableUnits100Sum"),
            get_value("affordableUnits120Sum"),
            get_value("affordableUnits140Sum"),
            get_value("affordableUnits150Sum"),
            get_value("affordableUnits170Sum"),
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
            get_value("countAffordable0BrSum"),
            get_value("countAffordable1BrSum"),
            get_value("countAffordable2BrSum"),
            get_value("countAffordable3BrSum"),
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
            get_value("unitsByTcacNotTcacSum"),  # Not TCAC
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
        net_units = get_value("netUnitsSum")

        # Extract fire hazard severity zone (FHSZ) data
        fire_hazard_high = get_value("unitsFireHazardHighSum")
        fire_hazard_very_high = get_value("unitsFireHazardVeryHighSum")
        fire_hazard_none = total_units - fire_hazard_high - fire_hazard_very_high

        fire_risk_values = [
            fire_hazard_none,  # No fire risk
            fire_hazard_high,  # High
            fire_hazard_very_high,  # Very High
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
            "net_units": net_units,
        }

    except Exception as e:
        st.error(f"Error processing aggregation data: {e}")
        import traceback

        st.error(traceback.format_exc())
        return None
