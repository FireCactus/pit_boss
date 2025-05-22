from typing import Type, TypeVar, Generic

T = TypeVar("T")


class Singleton(Generic[T]):
    def __init__(self, cls: Type[T]):
        self._cls = cls
        self._instance: T | None = None

    def __call__(self, *args, **kwargs) -> T:
        if self._instance is None:
            self._instance = self._cls(*args, **kwargs)
        return self._instance
