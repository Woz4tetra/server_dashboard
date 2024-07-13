import time
import streamlit as st
import pandas as pd
import numpy as np
from pprint import pprint
import psutil
from psutil._common import shwtemp


def main() -> None:
    st.set_page_config(layout='wide')
    # Add a selectbox to the sidebar:
    add_selectbox = st.sidebar.selectbox(
        'How would you like to be contacted?',
        ('Email', 'Home phone', 'Mobile phone')
    )

    # Add a slider to the sidebar:
    add_slider = st.sidebar.slider(
        'Select a range of values',
        0.0, 100.0, (25.0, 75.0)
    )

    all_temperatures = psutil.sensors_temperatures()
    sensors = {}
    for label, sensor_temps in all_temperatures.items():
        sensor_table = {'time': [pd.Timestamp.now().to_datetime64()]}
        for sensor_temp in sensor_temps:
            sensor_label = sensor_temp.label if sensor_temp.label else 'empty'
            if sensor_label in sensor_table:
                sensor_label = f'{sensor_label}_{np.random.randint(100)}'
            sensor_table[sensor_label] = [sensor_temp.current]
        sensors[label] = pd.DataFrame(sensor_table)


    with st.spinner('Updating...'):
        placeholder = st.empty()
        while True:
            with placeholder.container():
                all_temperatures = psutil.sensors_temperatures()
                for label, df in sensors.items():
                    sensor_temps = [sensor_temp.current for sensor_temp in all_temperatures.get(label, [])]
                    df.loc[len(df)] = [pd.Timestamp.now().to_datetime64()] + sensor_temps
                    st.line_chart(df, x='time')
                time.sleep(1)
