import pandas as pd
import streamlit as st
from plotly import graph_objects, subplots

from app.dashboard.draw_utils import format_df_time
from app.shared import CpuAggregatedData


def draw_cpu_aggregate_plot(
    cpu_agg_data: list[CpuAggregatedData], time_range: float | None
) -> None:
    if len(cpu_agg_data) == 0:
        return

    df = pd.DataFrame(
        [
            {
                "timestamp": data.timestamp,
                "Peak CPU Utilization": data.peak_utilization,
                "Peak Memory Usage": data.peak_memory_used,
                "Peak CPU Temperature": data.peak_temperature,
            }
            for data in cpu_agg_data
        ]
    )
    df = format_df_time(df, time_range)

    figure = subplots.make_subplots(
        rows=3,
        cols=1,
        subplot_titles=(
            "Peak CPU Utilization",
            "Peak Memory Usage",
            "Peak CPU Temperature",
        ),
    )

    figure.add_trace(
        graph_objects.Scatter(
            x=df["time"],
            y=df["Peak CPU Utilization"],
            name="Peak CPU Utilization",
            mode="lines",
        ),
        row=1,
        col=1,
    )

    figure.add_trace(
        graph_objects.Scatter(
            x=df["time"],
            y=df["Peak Memory Usage"],
            name="Peak Memory Usage",
            mode="lines",
        ),
        row=2,
        col=1,
    )

    figure.add_trace(
        graph_objects.Scatter(
            x=df["time"],
            y=df["Peak CPU Temperature"],
            name="Peak CPU Temperature",
            mode="lines",
        ),
        row=3,
        col=1,
    )
    figure.update_layout(height=700)

    st.plotly_chart(figure)
