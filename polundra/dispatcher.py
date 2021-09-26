import asyncio
import signal
import uuid
from functools import partial

from polundra.audio.pulse import Pulse
from polundra.audio.utils import read_wav_info
from polundra.utils import itertime, toggle_event
from polundra.visual.dbus import DBUS_BACKENDS, DBusManager
from polundra.visual.functions import f
from polundra.visual.screen import ScreenBrightness


async def keyboard_alert(event):
    fuck = DBusManager(**DBUS_BACKENDS['upower'])
    for v in map(partial(f, for_keyboard=True), itertime()):
        await event.wait()
        await asyncio.to_thread(setattr, fuck, 'value', v)
        await asyncio.sleep(1 / 60)


async def screen_alert(event):
    fuck = ScreenBrightness()
    for v in map(f, itertime()):
        await event.wait()
        await asyncio.to_thread(setattr, fuck, 'value', v)
        await asyncio.sleep(1 / 60)


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

    try:
        await asyncio.gather(audio_alert(event), keyboard_alert(event), screen_alert(event))
    except asyncio.CancelledError:
        exit()
