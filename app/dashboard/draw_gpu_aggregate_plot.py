import pandas as pd
import streamlit as st
from plotly import graph_objects, subplots
from plotly.colors import sequential

from app.dashboard.draw_utils import format_df_time
from app.shared import GpuAggregatedData


def draw_gpu_aggregate_plot(
    gpu_agg_data: dict[str, list[GpuAggregatedData]], time_range: float | None
) -> None:
    if len(gpu_agg_data) == 0:
        return

    figure = subplots.make_subplots(
        rows=4,
        cols=1,
        subplot_titles=(
            "Average GPU Utilization",
            "Average Memory Usage",
            "Average GPU Temperature",
            "Average Power Usage",
        ),
        shared_xaxes=True,
    )

    keys = sorted(list(gpu_agg_data.keys()))

    for key, gpu_data in gpu_agg_data.items():
        gpu_index = keys.index(key)
        gpu_name = f"GPU-{gpu_index}"
        line_color = sequential.Plasma[(gpu_index * 8) % len(sequential.Plasma)]

        df = pd.DataFrame(
            [
                {
                    "timestamp": data.timestamp,
                    "Average GPU Utilization": data.average_utilization_gpu,
                    "Average Memory Usage": data.average_memory_used,
                    "Average GPU Temperature": data.average_temperature_gpu,
                    "Average Power Usage": data.average_power_draw,
                }
                for data in gpu_data
            ]
        )
        df = format_df_time(df, time_range)
        df.sort_values(by="time", inplace=True)

        figure.add_trace(
            graph_objects.Scatter(
                x=df["time"],
                y=df["Average GPU Utilization"],
                name=f"{gpu_name} Average GPU Utilization (%)",
                mode="lines",
                line=dict(color=line_color),
            ),
            row=1,
            col=1,
        )

        figure.add_trace(
            graph_objects.Scatter(
                x=df["time"],
                y=df["Average Memory Usage"],
                name=f"{gpu_name} Average Memory Usage (MiB)",
                mode="lines",
                line=dict(color=line_color),
            ),
            row=2,
            col=1,
        )

        figure.add_trace(
            graph_objects.Scatter(
                x=df["time"],
                y=df["Average GPU Temperature"],
                name=f"{gpu_name} Average GPU Temperature (C)",
                mode="lines",
                line=dict(color=line_color),
            ),
            row=3,
            col=1,
        )

        figure.add_trace(
            graph_objects.Scatter(
                x=df["time"],
                y=df["Average Power Usage"],
                name=f"{gpu_name} Average Power Usage (W)",
                mode="lines",
                line=dict(color=line_color),
            ),
            row=4,
            col=1,
        )

    figure.update_layout(height=700)

    st.plotly_chart(figure)
