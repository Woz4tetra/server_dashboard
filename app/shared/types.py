from typing import TypeVar, Union

from app.shared.cpu_data import CpuAggregatedData, CpuData
from app.shared.gpu_data import GpuAggregatedData, GpuData
from app.shared.network_data import NetworkAggregatedData, NetworkData
from app.shared.ups_data import UpsAggregatedData, UpsData

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
