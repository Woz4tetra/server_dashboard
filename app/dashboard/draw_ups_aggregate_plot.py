import pandas as pd
import streamlit as st
from plotly import graph_objects, subplots

from app.dashboard.draw_utils import format_df_time
from app.shared.ups_data import UpsAggregatedData


def draw_ups_aggregate_plot(
    ups_agg_data: dict[str, list[UpsAggregatedData]], time_range: float | None
) -> None:
    if len(ups_agg_data) == 0:
        return

    figure = subplots.make_subplots(
        rows=2,
        cols=1,
        subplot_titles=(
            "Up percentage",
            "Peak Power",
        ),
    )

    for serial, ups_data in ups_agg_data.items():
        df = pd.DataFrame(
            [
                {
                    "timestamp": data.timestamp,
                    "Up percentage": data.up_percentage,
                    "Peak Power": data.peak_output_current * data.peak_output_voltage,
                }
                for data in ups_data
            ]
        )
        df = format_df_time(df, time_range)

        figure.add_trace(
            graph_objects.Scatter(
                x=df["time"],
                y=df["Up percentage"],
                mode="lines",
                name=f"{serial} Up percentage (%)",
            ),
            row=1,
            col=1,
        )

        figure.add_trace(
            graph_objects.Scatter(
                x=df["time"],
                y=df["Peak Power"],
                mode="lines",
                name=f"{serial} Peak Power (W)",
            ),
            row=2,
            col=1,
        )

    figure.update_layout(height=700)

    st.plotly_chart(figure)
