import pandas as pd
import streamlit as st
from plotly import graph_objects, subplots
from plotly.colors import sequential

from app.dashboard.draw_utils import format_df_time
from app.shared import NetworkData


def draw_network_plot(
    network_data: dict[str, list[NetworkData]], time_range: float
) -> None:
    if len(network_data) == 0:
        return

    figure = subplots.make_subplots(
        rows=2,
        cols=1,
        subplot_titles=("Ping",),
    )
    keys = sorted(list(network_data.keys()))

    for key, data in network_data.items():
        net_index = keys.index(key)
        line_color = sequential.Jet[(net_index * 8) % len(sequential.Jet)]

        df = pd.DataFrame(
            [
                {
                    "timestamp": data.timestamp,
                    "Ping (ms)": data.ping_ms,
                }
                for data in data
            ]
        )
        df = format_df_time(df, time_range)
        figure.add_trace(
            graph_objects.Scatter(
                x=df["time"],
                y=df["Ping (ms)"],
                mode="lines",
                name=f"{key} Ping (ms)",
                line=dict(color=line_color),
            ),
            row=1,
            col=1,
        )
    figure.update_layout(height=700)

    st.plotly_chart(figure)
