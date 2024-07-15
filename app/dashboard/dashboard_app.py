import logging
import time

import streamlit as st

from app.dashboard.data_vacuum import DataVacuum, load_bulk
from app.dashboard.draw_cpu_aggregate_plot import draw_cpu_aggregate_plot
from app.dashboard.draw_cpu_plot import draw_cpu_plot
from app.dashboard.draw_gpu_aggregate_plot import draw_gpu_aggregate_plot
from app.dashboard.draw_gpu_plot import draw_gpu_plot
from app.dashboard.draw_network_aggregate_plot import draw_network_aggregate_plot
from app.dashboard.draw_network_plot import draw_network_plot
from app.dashboard.draw_ups_aggregate_plot import draw_ups_aggregate_plot
from app.dashboard.draw_ups_plot import draw_ups_plot
from app.shared.initialize_logs import initialize_logs

APP = DataVacuum()
initialize_logs("frontend")


def main() -> None:
    logger = logging.getLogger("frontend")
    logger.info("Running frontend")
    st.set_page_config(layout="wide", page_title="Server Dashboard")

    st.title("Server Dashboard")

    show_aggregates = st.sidebar.checkbox("Show aggregates", value=False)
    plot_key = st.sidebar.selectbox(
        "Select plot",
        ["CPU", "GPU", "Network", "UPS"],
    )

    if plot_key is None:
        return

    if show_aggregates:
        aggregate_data = load_bulk()
        show_all = st.sidebar.checkbox("Show all", value=False)
        if show_all:
            time_range = None
        else:
            time_range = st.sidebar.slider("Plot time range (days)", 0.0, 60.0, 30.0)
            time_range *= 3600 * 24

        plot_function, plot_data = {
            "CPU": (draw_cpu_aggregate_plot, aggregate_data.cpu),
            "GPU": (draw_gpu_aggregate_plot, aggregate_data.gpu),
            "Network": (draw_network_aggregate_plot, aggregate_data.network),
            "UPS": (draw_ups_aggregate_plot, aggregate_data.ups),
        }[plot_key]

        plot_function(plot_data, time_range)
    else:
        time_range = st.sidebar.slider("Plot time range (hours)", 0.05, 24.0, 1.0)
        time_range *= 3600

        plot_function, plot_data = {
            "CPU": (draw_cpu_plot, APP.cpu_data),
            "GPU": (draw_gpu_plot, APP.gpu_data),
            "Network": (draw_network_plot, APP.network_data),
            "UPS": (draw_ups_plot, APP.ups_data),
        }[plot_key]

        if st.sidebar.toggle("Live update"):
            with st.spinner("Updating..."):
                placeholder = st.empty()
                while True:
                    APP.update()
                    with placeholder.container():
                        plot_function(plot_data, time_range)
                    time.sleep(1.0)
        elif st.sidebar.button("Update"):
            APP.update()
            plot_function(plot_data, time_range)
        else:
            APP.update()
            plot_function(plot_data, time_range)
