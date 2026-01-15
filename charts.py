"""
Chart creation functions for the zoning report card dashboard.
"""

import plotly.graph_objects as go


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

    # Color scheme for scenarios
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
