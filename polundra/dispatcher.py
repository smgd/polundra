import asyncio
import signal
import uuid
import logging

from functools import partial

from polundra.audio.pulse import Pulse
from polundra.audio.utils import read_wav_info
from polundra.utils import itertime, toggle_event
from polundra.visual.dbus import DBUS_BACKENDS, DBusManager
from polundra.visual.functions import f_kbd, f_scr
from polundra.visual.screen import ScreenBrightness

logger = logging.getLogger(__name__)

def _update_backend(backend, value):
    backend.value = value

async def run_backend(event, f, backend):

    for x in itertime():
        await event.wait()
        y = f(x)
        logger.debug(f'set backend {backend!r} to f({x!r}) = {y!r}')
        await asyncio.to_thread(_update_backend, ackend, y)
        await asyncio.sleep(1 / 60)


async def keyboard_alert(event):
    fuck = DBusManager(**DBUS_BACKENDS['upower'])
    await run_backend(event, f_kbd, fuck)


async def screen_alert(event):
    fuck = ScreenBrightness()
    await run_backend(event, f_scr, fuck)


async def audio_alert(event, path='assets/alert.wav'):
    async with Pulse() as pa:
        sample_name = str(uuid.uuid4())

        await pa.upload_sample(path, sample_name)
        info = await asyncio.to_thread(read_wav_info, path)
        delay = info.nframes / info.framerate
        while True:
            await event.wait()
            await pa.play_sample(sample_name)
            await asyncio.sleep(delay)


async def run():
    event = asyncio.Event()
    event.set()
    loop = asyncio.get_running_loop()
    current_task = asyncio.current_task()
    loop.add_signal_handler(signal.SIGALRM, lambda *_: toggle_event(event))
    loop.add_signal_handler(signal.SIGINT, lambda *_: loop.call_soon(current_task.cancel))

    backends = audio_alert, keyboard_alert, screen_alert
    coros = [b(event) for b in backends]
    tasks = [asyncio.create_task(coro) for coro in coros]
    try:
        await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)
    except asyncio.CancelledError:
        exit()
