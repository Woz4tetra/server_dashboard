from typing import TypeVar, Union

from app.shared_data.cpu_data import CpuAggregatedData, CpuData
from app.shared_data.gpu_data import GpuAggregatedData, GpuData
from app.shared_data.network_data import NetworkAggregatedData, NetworkData
from app.shared_data.ups_data import UpsAggregatedData, UpsData

DataImpl = Union[
    CpuData,
    NetworkData,
    GpuData,
    UpsData,
]

AggregateImpl = Union[
    CpuAggregatedData,
    NetworkAggregatedData,
    GpuAggregatedData,
    UpsAggregatedData,
]

DataType = TypeVar("DataType", bound=DataImpl)

AggregateType = TypeVar("AggregateType", bound=AggregateImpl)
