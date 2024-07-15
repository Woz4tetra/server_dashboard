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
            "Peak GPU Utilization",
            "Peak Memory Usage",
            "Peak GPU Temperature",
            "Peak Power Usage",
        ),
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
                    "Peak GPU Utilization": data.peak_utilization_gpu,
                    "Peak Memory Usage": data.peak_memory_used,
                    "Peak GPU Temperature": data.peak_temperature_gpu,
                    "Peak Power Usage": data.peak_power_draw,
                }
                for data in gpu_data
            ]
        )
        df = format_df_time(df, time_range)

        figure.add_trace(
            graph_objects.Scatter(
                x=df["time"],
                y=df["Peak GPU Utilization"],
                name=f"{gpu_name} Peak GPU Utilization (%)",
                mode="lines",
                line=dict(color=line_color),
            ),
            row=1,
            col=1,
        )

        figure.add_trace(
            graph_objects.Scatter(
                x=df["time"],
                y=df["Peak Memory Usage"],
                name=f"{gpu_name} Peak Memory Usage (MiB)",
                mode="lines",
                line=dict(color=line_color),
            ),
            row=2,
            col=1,
        )

        figure.add_trace(
            graph_objects.Scatter(
                x=df["time"],
                y=df["Peak GPU Temperature"],
                name=f"{gpu_name} Peak GPU Temperature (C)",
                mode="lines",
                line=dict(color=line_color),
            ),
            row=3,
            col=1,
        )

        figure.add_trace(
            graph_objects.Scatter(
                x=df["time"],
                y=df["Peak Power Usage"],
                name=f"{gpu_name} Peak Power Usage (W)",
                mode="lines",
                line=dict(color=line_color),
            ),
            row=4,
            col=1,
        )

    figure.update_layout(height=700)

    st.plotly_chart(figure)
