import pandas as pd
import streamlit as st
from plotly import graph_objects, subplots
from plotly.colors import sequential

from app.dashboard.draw_utils import format_df_time
from app.shared.network_data import NetworkAggregatedData


def draw_network_aggregate_plot(
    net_agg_data: dict[str, list[NetworkAggregatedData]], time_range: float | None
) -> None:
    if len(net_agg_data) == 0:
        return

    figure = subplots.make_subplots(
        rows=2,
        cols=1,
        subplot_titles=(
            "Num misses",
            "Peak Ping",
        ),
        shared_xaxes=True,
    )

    keys = sorted(list(net_agg_data.keys()))

    for key, net_data in net_agg_data.items():
        net_index = keys.index(key)
        line_color = sequential.Jet[(net_index * 8) % len(sequential.Jet)]

        df = pd.DataFrame(
            [
                {
                    "timestamp": data.timestamp,
                    "Num misses": data.num_pings - data.num_hits,
                    "Num pings": data.num_pings,
                    "Percent packet loss": data.percent_packet_loss,
                    "Ping (ms)": data.peak_ping,
                }
                for data in net_data
            ]
        )
        df = format_df_time(df, time_range)

        text = df.apply(
            lambda x: f"Num pings: {x['Num pings']}. "
            f"Num misses: {x['Num misses']}. "
            f"Percent packet loss: {x['Percent packet loss']:.6f}%",
            axis=1,
        )

        figure.add_trace(
            graph_objects.Scatter(
                x=df["time"],
                y=df["Num misses"],
                name=f"{key} Num misses",
                mode="lines",
                text=text,
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
