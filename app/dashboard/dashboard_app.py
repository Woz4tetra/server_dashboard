import logging

import streamlit as st

from app.dashboard.data_vacuum import load_bulk, load_today
from app.dashboard.draw_cpu_aggregate_plot import draw_cpu_aggregate_plot
from app.dashboard.draw_cpu_plot import draw_cpu_plot
from app.dashboard.draw_gpu_aggregate_plot import draw_gpu_aggregate_plot
from app.dashboard.draw_gpu_plot import draw_gpu_plot
from app.dashboard.draw_network_aggregate_plot import draw_network_aggregate_plot
from app.dashboard.draw_network_plot import draw_network_plot
from app.dashboard.draw_ups_aggregate_plot import draw_ups_aggregate_plot
from app.dashboard.draw_ups_plot import draw_ups_plot
from app.shared.initialize_logs import initialize_logs

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
        logger.error("No plot key selected")
        return

    if st.sidebar.button("Update"):
        pass

    if show_aggregates:
        logger.debug("Showing aggregates")
        aggregate_data = load_bulk()
        show_all = st.sidebar.checkbox("Show all", value=False)
        if show_all:
            logger.debug("Showing all data")
            time_range = None
        else:
            time_range = st.sidebar.slider("Plot time range (days)", 0.0, 60.0, 30.0)
            time_range *= 3600 * 24
            logger.debug(f"Aggregate time range: {time_range}")

        plot_function, plot_data = {
            "CPU": (draw_cpu_aggregate_plot, aggregate_data.cpu),
            "GPU": (draw_gpu_aggregate_plot, aggregate_data.gpu),
            "Network": (draw_network_aggregate_plot, aggregate_data.network),
            "UPS": (draw_ups_aggregate_plot, aggregate_data.ups),
        }[plot_key]

        plot_function(plot_data, time_range)
    else:
        logger.debug("Showing today's data")
        with st.spinner("Loading data..."):
            todays_data = load_today()
        time_range = st.sidebar.slider("Plot time range (hours)", 0.05, 24.0, 1.0)
        time_range *= 3600
        logger.debug(f"Today time range: {time_range}")

        plot_function, plot_data = {
            "CPU": (draw_cpu_plot, todays_data.cpu),
            "GPU": (draw_gpu_plot, todays_data.gpu),
            "Network": (draw_network_plot, todays_data.network),
            "UPS": (draw_ups_plot, todays_data.ups),
        }[plot_key]

        with st.spinner("Rendering plots..."):
            plot_function(plot_data, time_range)
