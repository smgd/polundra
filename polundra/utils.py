import asyncio
import time


def itertime():
    return iter(time.monotonic, 0)


def toggle_event(event: asyncio.Event) -> None:
    if event.is_set():
        event.clear()
    else:
        event.set()
