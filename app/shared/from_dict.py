from enum import Enum
from typing import Type, TypeVar

from dacite import Config
from dacite import from_dict as from_dict_dacite

T = TypeVar("T")


def from_dict(cls: Type[T], data: dict) -> T:
    return from_dict_dacite(data_class=cls, data=data, config=Config(cast=[Enum]))
