"""
Color schemes for charts in the zoning report card dashboard.
"""

# Chart color schemes
total_feasibility_color = "#D66E6C"

income_bracket_colors = {
    "Market rate <=50% MFI": "#5DBDB4",
    "Market rate 51%-100% MFI": "#F07D4A",
    "Market rate 101-150% MFI": "#6FB573",
    "Market rate 151-200% MFI": "#F4C04E",
    "Market rate 201-250% MFI": "#D66E6C",
    "Market rate >251% MFI": "#6B9BD1",
    "Affordable <=50% AMI": "#9FE0DA",
    "Affordable 50-80% AMI": "#A8D5A8",
    "Affordable 80-100% AMI": "#F9DD8F",
    "Affordable 100-120% AMI": "#A5C5E5",
    "Affordable 120%+ AMI": "#B8E0D8",
}

bedroom_count_colors = {
    "0 bedrooms": "#6FB573",
    "1 bedroom": "#F4C04E",
    "2 bedrooms": "#D66E6C",
    "3+ bedrooms": "#6B9BD1",
    "Affordable 0 bedrooms": "#A8D5A8",
    "Affordable 1 bedroom": "#F9DD8F",
    "Affordable 2 bedrooms": "#E8A5A3",
    "Affordable 3+ bedrooms": "#A5C5E5",
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
    "sf": "#6B9BD1",
    "mf": "#F07D4A",
    "th": "#6FB573",
    "plex": "#F4C04E",
}

tcac_colors = {
    "Low": "#D66E6C",
    "Moderate": "#F4C04E",
    "High": "#6FB573",
    "Highest": "#6B9BD1",
    "Not TCAC": "#5DBDB4",
}

fire_risk_colors = {
    "None": "#6FB573",
    "High": "#F4C04E",
    "Very High": "#D66E6C",
}
