import contextlib
import typing

from app.main import app


@contextlib.contextmanager
def use_dependency(
    key: typing.Callable[..., typing.Any],
    value: typing.Callable[..., typing.Any],
) -> typing.Generator[None, None, None]:
    """
    Overide dependency with stubs during test
    """
    original_value = app.dependency_overrides.get(key)
    app.dependency_overrides[key] = value

    try:
        yield
    finally:
        if original_value is None:
            del app.dependency_overrides[key]
        else:
            app.dependency_overrides[key] = original_value
