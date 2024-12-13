from typing import TypeVar

SingletonType = TypeVar("SingletonType", bound="Singleton")


class SingletonMeta(type):
    _instance: SingletonType

    def __init__(self, *args, **kwds) -> None:
        self._instance = super().__call__()

    def __call__(self) -> SingletonType:
        return self._instance


class Singleton(metaclass=SingletonMeta):
    ...
