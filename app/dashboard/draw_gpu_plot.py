import pandas as pd
import streamlit as st
from plotly import graph_objects, subplots
from plotly.colors import sequential

from app.dashboard.draw_utils import format_df_time
from app.shared_data import GpuData


def draw_gpu_plot(all_gpu_data: dict[str, list[GpuData]], time_range: float) -> None:
    if len(all_gpu_data) == 0:
        return

    figure = subplots.make_subplots(
        rows=4,
        cols=1,
        subplot_titles=("GPU Utilization", "Memory Usage", "GPU Temperature", "Power"),
    )

    keys = sorted(list(all_gpu_data.keys()))

    for key, gpu_data in all_gpu_data.items():
        gpu_index = keys.index(key)
        gpu_name = f"GPU-{gpu_index}"
        line_color = sequential.Plasma[(gpu_index * 8) % len(sequential.Plasma)]
        df = pd.DataFrame(
            [
                {
                    "timestamp": data.timestamp,
                    r"GPU%": data.utilization_gpu,
                    "Memory used (MiB)": data.memory_used,
                    "Temperature (C)": data.temperature_gpu,
                    "Power (W)": data.power_draw,
                }
                for data in gpu_data
            ]
        )
        df = format_df_time(df, time_range)
        figure.add_trace(
            graph_objects.Scatter(
                x=df["time"],
                y=df[r"GPU%"],
                mode="lines",
                name=f"{gpu_name} %",
                line=dict(color=line_color),
            ),
            row=1,
            col=1,
        )
        figure.add_trace(
            graph_objects.Scatter(
                x=df["time"],
                y=df["Memory used (MiB)"],
                mode="lines",
                name=f"{gpu_name} Memory used (MiB)",
                line=dict(color=line_color),
            ),
            row=2,
            col=1,
        )
        figure.add_trace(
            graph_objects.Scatter(
                x=df["time"],
                y=df["Temperature (C)"],
                mode="lines",
                name=f"{gpu_name} Temperature (C)",
                line=dict(color=line_color),
            ),
            row=3,
            col=1,
        )
        figure.add_trace(
            graph_objects.Scatter(
                x=df["time"],
                y=df["Power (W)"],
                mode="lines",
                name=f"{gpu_name} Power (W)",
                line=dict(color=line_color),
            ),
            row=4,
            col=1,
        )
    figure.update_layout(height=700)

    st.plotly_chart(figure)
