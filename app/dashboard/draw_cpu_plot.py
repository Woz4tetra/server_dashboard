import pandas as pd
import streamlit as st
from plotly import graph_objects, subplots

from app.dashboard.draw_utils import format_df_time
from app.shared import CpuData


def draw_cpu_plot(cpu_data: list[CpuData], time_range: float) -> None:
    if len(cpu_data) == 0:
        return
    df = pd.DataFrame(
        [
            {
                "timestamp": data.timestamp,
                r"CPU%": data.utilization,
                "Memory used (MiB)": data.memory_used,
                "Temperature (C)": data.temperature,
            }
            for data in cpu_data
        ]
    )

    df = format_df_time(df, time_range)

    cpu_df = df[["time", r"CPU%"]]
    memory_df = df[["time", "Memory used (MiB)"]]
    temp_df = df[["time", "Temperature (C)"]]

    figure = subplots.make_subplots(
        rows=3,
        cols=1,
        subplot_titles=("CPU Utilization", "Memory Usage", "CPU Temperature"),
    )
    figure.add_trace(
        graph_objects.Scatter(
            x=cpu_df["time"], y=cpu_df[r"CPU%"], mode="lines", name=r"CPU %"
        ),
        row=1,
        col=1,
    )
    figure.add_trace(
        graph_objects.Scatter(
            x=memory_df["time"],
            y=memory_df["Memory used (MiB)"],
            mode="lines",
            name="Memory used (MiB)",
        ),
        row=2,
        col=1,
    )
    figure.add_trace(
        graph_objects.Scatter(
            x=temp_df["time"],
            y=temp_df["Temperature (C)"],
            mode="lines",
            name="Temperature (C)",
        ),
        row=3,
        col=1,
    )
    figure.update_layout(height=700)

    st.plotly_chart(figure)
