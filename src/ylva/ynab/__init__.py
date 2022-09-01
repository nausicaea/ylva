from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass
class ResponseWrapper(Generic[T]):
    data: T


@dataclass
class RequestWrapper(Generic[T]):
    data: T
