from typing import Optional, TypeVar, Generic

T = TypeVar("T")
E = TypeVar("E")


class Result(Generic[T, E]):
    def __init__(self, data: Optional[T] = None, error: Optional[E] = None) -> None:
        assert (data and not error) or (not data and error)
        self.data = data
        self.error = error

    def unwrap(self) -> T:
        assert self.data
        return self.data

    def unwrap_err(self) -> E:
        assert self.error
        return self.error

    def ok(self) -> Optional[T]:
        return self.data

    def err(self) -> Optional[E]:
        return self.error

    def good(self) -> bool:
        return self.data is not None

    def bad(self) -> bool:
        return self.error is not None


class Ok(Result[T, E]):
    def __init__(self, data: T) -> None:
        super().__init__(data)


class Err(Result[T, E]):
    def __init__(self, error: E) -> None:
        super().__init__(error=error)
