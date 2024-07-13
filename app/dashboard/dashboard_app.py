import json
import os
import time
from io import BufferedReader
from queue import Queue
from threading import Lock, Thread
from typing import Generator

import pandas as pd
import streamlit as st
from plotly import graph_objects, subplots

from app.shared_data import (
    CpuAggregatedData,
    CpuData,
    GpuAggregatedData,
    GpuData,
    NetworkAggregatedData,
    NetworkData,
    UpsAggregatedData,
    UpsData,
)
from app.shared_data.aggregate_utils import get_data_class, group_by_key, group_by_type
from app.shared_data.constants import TODAYS_DATA
from app.shared_data.types import DataImpl


def follow(fp: BufferedReader) -> Generator[bytes, None, None]:
    """generator function that yields new lines in a file"""

    while True:
        line = fp.readline()
        if not line:
            time.sleep(0.1)
            continue
        yield line


def follow_task(fp: BufferedReader, queue: Queue, lock: Lock) -> None:
    for line in follow(fp):
        with lock:
            queue.put(line)


class App:
    def __init__(self) -> None:
        self.cpu_data = []
        self.gpu_data: dict[str, list[GpuData]] = {}
        self.network_data: dict[str, list[NetworkData]] = {}
        self.ups_data: dict[str, list[UpsData]] = {}

        fp = open(TODAYS_DATA, "rb")
        self.line_queue: Queue[bytes] = Queue()
        self.data_lock = Lock()
        follow_thread = Thread(
            target=follow_task, args=(fp, self.line_queue, self.data_lock), daemon=True
        )
        follow_thread.start()

    def wait_for_data(self) -> None:
        while self.line_queue.empty():
            time.sleep(0.1)

    def update(self) -> None:
        self.wait_for_data()
        data = []
        with self.data_lock:
            while not self.line_queue.empty():
                line = self.line_queue.get()
                data_dict = json.loads(line)
                row = get_data_class(data_dict).from_dict(data_dict)
                data.append(row)

        grouped_by_type = group_by_type(data)

        self.cpu_data.extend(grouped_by_type.get("CpuData", []))

        gpu_data_by_key = group_by_key(grouped_by_type.get("GpuData", []), "uuid")
        for key, value in gpu_data_by_key.items():
            self.gpu_data.setdefault(key, []).extend(value)  # type: ignore

        network_data_by_key = group_by_key(
            grouped_by_type.get("NetworkData", []), "destination"
        )
        for key, value in network_data_by_key.items():
            self.network_data.setdefault(key, []).extend(value)  # type: ignore

        ups_data_by_key = group_by_key(grouped_by_type.get("UpsData", []), "serial")
        for key, value in ups_data_by_key.items():
            self.ups_data.setdefault(key, []).extend(value)  # type: ignore


def draw_cpu_plot(cpu_data: list[CpuData], time_range: float) -> None:
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
    if df.empty:
        return

    df = df[df["timestamp"] > time.time() - time_range]

    df["time"] = pd.to_datetime(df["timestamp"], unit="s")
    df.drop(columns=["timestamp"], inplace=True)
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
    figure.update_layout(
        height=800,
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="left", x=0.01),
    )

    st.plotly_chart(figure)


def draw_gpu_plot(gpu_data: list[GpuData], time_range: float) -> None:
    pass


def draw_network_plot(network_data: list[NetworkData], time_range: float) -> None:
    pass


def draw_ups_plot(ups_data: list[UpsData], time_range: float) -> None:
    pass


APP = App()


def main() -> None:
    st.set_page_config(layout="wide")

    st.title("Server Dashboard")

    time_range = st.sidebar.slider("Plot time range (minutes)", 0.0, 60.0, 1.0)
    time_range *= 60

    show_aggregates = st.sidebar.checkbox("Show aggregates", value=False)
    plot_key = st.sidebar.selectbox(
        "Select plot",
        ["CPU", "GPU", "Network", "UPS"],
    )

    if show_aggregates:
        pass
    else:
        if plot_key is None:
            return
        plot_function, plot_data = {
            "CPU": (draw_cpu_plot, APP.cpu_data),
            "GPU": (draw_gpu_plot, APP.gpu_data),
            "Network": (draw_network_plot, APP.network_data),
            "UPS": (draw_ups_plot, APP.ups_data),
        }[plot_key]

        if st.toggle("Live update"):
            with st.spinner("Updating..."):
                placeholder = st.empty()
                while True:
                    APP.update()
                    with placeholder.container():
                        plot_function(plot_data, time_range)
                    time.sleep(1.0)
        elif st.button("Update"):
            APP.update()
            plot_function(plot_data, time_range)
        else:
            APP.update()
            plot_function(plot_data, time_range)
