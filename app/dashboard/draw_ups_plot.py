import pandas as pd
import streamlit as st
from plotly import graph_objects, subplots

from app.dashboard.draw_utils import format_df_time
from app.shared import UpsData


def find_status_transitions(df: pd.DataFrame) -> list[tuple[float, str]]:
    unique_statuses = [status for status in df["Status"].unique()]
    df["index"] = df["Status"].apply(lambda x: unique_statuses.index(x))
    df["diff"] = df["index"].diff()
    transitions = df[df["diff"] != 0]
    return list(zip(transitions["time"], transitions["Status"]))


def draw_ups_plot(all_ups_data: list[UpsData], time_range: float) -> None:
    if len(all_ups_data) == 0:
        return

    figure = subplots.make_subplots(
        rows=2,
        cols=1,
        subplot_titles=("Status", "Power"),
        shared_xaxes=True,
    )

    df = pd.DataFrame(
        [
            {
                "timestamp": data.timestamp,
                "Status": data.status,
                "Power (W)": data.output_current * data.output_voltage,
            }
            for data in all_ups_data
        ]
    )
    df = format_df_time(df, time_range)
    if df.empty:
        return
    df.sort_values(by="time", inplace=True)

    transitions = find_status_transitions(df)
    transitions.append((df["time"].max(), df["Status"].iloc[-1]))

    figure.add_trace(
        graph_objects.Scatter(
            x=[time for time, _ in transitions],
            y=[0 for _ in transitions],
            mode="lines+markers",
            name="Status",
            text=transitions,
            yaxis="y2",
        ),
        row=1,
        col=1,
    )
    figure.update_traces(mode="markers+lines", hovertemplate=None)
    figure.update_layout(hovermode="x unified")

    figure.add_trace(
        graph_objects.Scatter(
            x=df["time"],
            y=df["Power (W)"],
            mode="lines",
            name="Power (W)",
        ),
        row=2,
        col=1,
    )
    figure.update_layout(height=700)

    st.plotly_chart(figure)
