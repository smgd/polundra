from decimal import Decimal
from pathlib import Path
from typing import Type, Any
import asyncio
import dbus
import math
import os
import pulsectl
import signal
import time
import uuid
import wave


DBUS_BACKENDS = {
    'systemd': {
        'name': 'org.freedesktop.login1',
        'path': '/org/freedesktop/login1/session/auto',
        'interface': 'org.freedesktop.login1.session',
        'getter': 'GetBrightness',
        'setter': 'SetBrightness',
        # 'max_getter': 'GetMaxBrightness',
    },        
    'gnome': {
        'name': 'org.gnome.SettingsDaemon.Power',
        'path': '/org/gnome/SettingsDaemon/Power',
        'interface': 'org.gnome.SettingsDaemon.Power.Screen',
        'getter': 'GetPercentage',
        'setter': 'SetPercentage',
    },
    'upower': {
        'name': 'org.freedesktop.UPower',
        'path': '/org/freedesktop/UPower/KbdBacklight',
        'interface': 'org.freedesktop.UPower.KbdBacklight',
        'getter': 'GetBrightness',
        'setter': 'SetBrightness',
        'max_getter': 'GetMaxBrightness',
    },
}


class DBusBrightnessManager:
    def __init__(self, name, path, interface, getter, setter, max_getter=None) -> None:
        self.bus = dbus.SystemBus()
        self.proxy = self.bus.get_object(name, path)
        self.iface = dbus.Interface(self.proxy, interface)
        self.getter = getattr(self.iface, getter)
        self.setter = getattr(self.iface, setter)
        self.max_getter = getattr(self.iface, max_getter) if max_getter else (lambda: 100)
        
    @property
    def current(self) -> int:
        return self.getter()

    @current.setter
    def current(self, value: int) -> None:
        return self.setter(value)

    @property
    def maximum(self) -> int:
        return self.max_getter()

    @property
    def value(self) -> Decimal:
        return Decimal(self.current) / Decimal(self.maximum)

    @value.setter
    def value(self, v) -> None:
        self.current = int(v * self.maximum)


class Brightness:
    def __init__(self):
        self.kbd = DBusBrightnessManager(**DBUS_BACKENDS['upower'])
        self.scr = DBusBrightnessManager(**DBUS_BACKENDS['systemd'])

    @property
    def value(self):
        return self.scr.value

    @value.setter
    def value(self, v):
        try:
            self.kbd.value = v
        except:
            pass
        try:
            self.scr.value = v
        except:
            pass

def f(v):
    return 0.05 + 0.95 * (0.5 + 0.45 * math.sin(2 * math.pi * v))

def itertime():
    return iter(time.monotonic, 0)


async def visual_alert(event):
    brightness = Brightness()
    for v in map(f, itertime()):
        await event.wait()
        await asyncio.to_thread(setattr, brightness, 'value', v)
        await asyncio.sleep(1/60)


class Pulse(pulsectl.Pulse):
    async def __aenter__(self):
        await asyncio.to_thread(self.__enter__)
        return self

    async def __aexit__(self, *exc_info):
        await asyncio.to_thread(self.__exit__, *exc_info)


    async def upload_sample(self, filename, name):
        return await asyncio.to_thread(self._upload_sample, filename, name)

    def _upload_sample(self, filename, name):
        import subprocess
        with subprocess.Popen(['pactl', 'upload-sample', filename, name]) as proc:
            proc.wait()


    async def play_sample(self, name):
        return await asyncio.to_thread(super().play_sample, name)

def read_wav_info(path) -> wave._wave_params:
    with wave.open(path) as wav:
        return wav.getparams()



async def audio_alert(event, path='alert.wav'):
    async with Pulse() as pa:
        sample_name = str(uuid.uuid4())

        await pa.upload_sample(path, sample_name)
        info = await asyncio.to_thread(read_wav_info, path)
        delay = info.nframes / info.framerate
        while True:
            await event.wait()
            await pa.play_sample(sample_name)
            await asyncio.sleep(delay)

def toggle(event):
    if event.is_set():
        event.clear()
    else:
        event.set()

async def main():
    event = asyncio.Event()
    event.set()
    loop = asyncio.get_running_loop()
    loop.add_signal_handler(signal.SIGALRM, lambda *_: toggle(event))
    await asyncio.gather(audio_alert(event), visual_alert(event))

if __name__ == '__main__':
    asyncio.run(main(), debug=1)
