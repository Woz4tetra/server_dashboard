import pandas as pd
import streamlit as st
from plotly import graph_objects, subplots
from plotly.colors import sequential

from app.dashboard.draw_utils import format_df_time
from app.shared_data.network_data import NetworkAggregatedData


def draw_network_aggregate_plot(
    net_agg_data: dict[str, list[NetworkAggregatedData]], time_range: float | None
) -> None:
    if len(net_agg_data) == 0:
        return

    figure = subplots.make_subplots(
        rows=2,
        cols=1,
        subplot_titles=(
            "Percent Packet Loss",
            "Peak Ping",
        ),
    )

    keys = sorted(list(net_agg_data.keys()))

    for key, net_data in net_agg_data.items():
        net_index = keys.index(key)
        line_color = sequential.Jet[(net_index * 8) % len(sequential.Jet)]

        df = pd.DataFrame(
            [
                {
                    "timestamp": data.timestamp,
                    "Percent Packet Loss": data.percent_packet_loss,
                    "Ping (ms)": data.peak_ping,
                }
                for data in net_data
            ]
        )
        df = format_df_time(df, time_range)

        figure.add_trace(
            graph_objects.Scatter(
                x=df["time"],
                y=df["Percent Packet Loss"],
                name=f"{key} Percent Packet Loss (%)",
                mode="lines",
                line=dict(color=line_color),
            ),
            row=1,
            col=1,
        )

        figure.add_trace(
            graph_objects.Scatter(
                x=df["time"],
                y=df["Ping (ms)"],
                name=f"{key} Peak Ping (ms)",
                mode="lines",
                line=dict(color=line_color),
            ),
            row=2,
            col=1,
        )

    figure.update_layout(height=700)

    st.plotly_chart(figure)
