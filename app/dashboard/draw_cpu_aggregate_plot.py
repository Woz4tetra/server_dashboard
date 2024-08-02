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
                "Average CPU Utilization": data.average_utilization,
                "Average Memory Usage": data.average_memory_used,
                "Average CPU Temperature": data.average_temperature,
            }
            for data in cpu_agg_data
        ]
    )
    df = format_df_time(df, time_range)
    df.sort_values(by="time", inplace=True)

    figure = subplots.make_subplots(
        rows=3,
        cols=1,
        subplot_titles=(
            "Average CPU Utilization",
            "Average Memory Usage",
            "Average CPU Temperature",
        ),
        shared_xaxes=True,
    )

    figure.add_trace(
        graph_objects.Scatter(
            x=df["time"],
            y=df["Average CPU Utilization"],
            name="Average CPU Utilization",
            mode="lines",
        ),
        row=1,
        col=1,
    )

    figure.add_trace(
        graph_objects.Scatter(
            x=df["time"],
            y=df["Average Memory Usage"],
            name="Average Memory Usage",
            mode="lines",
        ),
        row=2,
        col=1,
    )

    figure.add_trace(
        graph_objects.Scatter(
            x=df["time"],
            y=df["Average CPU Temperature"],
            name="Average CPU Temperature",
            mode="lines",
        ),
        row=3,
        col=1,
    )
    figure.update_layout(height=700)

    st.plotly_chart(figure)
