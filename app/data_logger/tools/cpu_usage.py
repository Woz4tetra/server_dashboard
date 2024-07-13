import datetime

import numpy as np
import psutil

from app.shared_data.cpu_data import CpuData


def get_cpu_temperatures() -> list[float]:
    temp_sensors = psutil.sensors_temperatures()
    # the priority for CPU temp is as follows: coretemp sensor -> sensor with CPU in the label -> acpi -> k10temp
    if "coretemp" in temp_sensors:
        return [temp.current for temp in temp_sensors["coretemp"]]

    temperatures = []
    # iterate over all sensors
    for sensor in temp_sensors:
        # iterate over all temperatures in the current sensor
        for temp in temp_sensors[sensor]:
            if "CPU" in temp.label and temp.current != 0:
                temperatures.append(temp.current)
    if len(temperatures) == 0:
        for sensor in ["acpitz", "k10temp", "zenpower"]:
            if sensor in temp_sensors and temp_sensors[sensor][0].current != 0:
                temperatures.append(temp_sensors[sensor][0].current)
    return temperatures


def cpu_usage() -> CpuData:
    cpu_percent = psutil.cpu_percent()
    virtual_memory = psutil.virtual_memory()
    virtual_memory_free = virtual_memory.free / 1024**2
    virtual_memory_used = virtual_memory.used / 1024**2
    average_temperature = float(np.mean(get_cpu_temperatures()))
    return CpuData(
        timestamp=datetime.datetime.now().timestamp(),
        utilization=cpu_percent,
        memory_used=virtual_memory_used,
        memory_free=virtual_memory_free,
        temperature=average_temperature,
    )
