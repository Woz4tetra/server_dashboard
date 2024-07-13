from typing import Protocol, Type, TypeVar

T = TypeVar("T")


class DataInterface(Protocol):
    def to_dict(self) -> dict: ...

    @classmethod
    def from_dict(cls: Type[T], data: dict) -> T: ...
