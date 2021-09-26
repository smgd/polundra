import asyncio
import time
from contextlib import contextmanager, asynccontextmanager
from functools import wraps
from typing import Generator


def itertime():
    return iter(time.monotonic, 0)


def toggle_event(event: asyncio.Event) -> None:
    if event.is_set():
        event.clear()
    else:
        event.set()


@contextmanager
def restore_value(backend) -> Generator[None, None, None]:
    value = backend.value
    try:
        yield
    finally:
        backend.value = value


def sync_to_async(func):
    @wraps(func)
    async def wrapper(*args, **kwds):
        return await asyncio.to_thread(func, *args, **kwds)
    return wrapper


@asynccontextmanager
async def sync_to_async_cm(cm):
    res = await sync_to_async(cm.__enter__)()
    try:
        yield res
    except Exception as e:
        if not await sync_to_async(cm.__exit__)(type(e), e, e.__traceback__):
            raise
    else:
        await sync_to_async(cm.__exit__)(None, None, None)


def sync_to_async_contextmanager(func):
    @wraps(func)
    def wrapper(*args, **kwds):
        return sync_to_async_cm(func(*args, **kwds))
    return wrapper


restore_value_async = sync_to_async_contextmanager(restore_value)
