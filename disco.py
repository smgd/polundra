from decimal import Decimal
from pathlib import Path
from typing import Type, Any

import asyncio
import math
import os
import pulsectl
import time
import uuid
import wave


class FileVar:
    def __init__(self, path: str, type_: Type[Any] = str) -> None:
        self.path: Path = Path(path)
        self.type_ = type_

    def get(self):
        return self.type_(self.path.read_text())

    def set(self, value):
        return self.path.write_text(str(value))


class FileProperty:
    def __init__(self, var: FileVar) -> None:
        self.var = var

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return self.var.get()

    def __set__(self, instance, value):
        self.var.set(value)


class Brightness:
    maximal = FileProperty(FileVar('/sys/class/backlight/intel_backlight/max_brightness', int))
    current = FileProperty(FileVar('/sys/class/backlight/intel_backlight/brightness', int))



    @property
    def value(self) -> Decimal:
        return Decimal(self.current) / Decimal(self.maximal)

    @value.setter
    def value(self, v) -> None:
        self.current = int(v * self.maximal)



def f(v):
    return 0.05 + 0.95 * (0.5 + 0.45 * math.sin(2 * math.pi * v))

def itertime():
    return iter(time.monotonic, 0)


async def visual_alert():
    brightness = Brightness()
    for v in map(f, itertime()):
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



async def audio_alert(path='alert.wav'):
    async with Pulse() as pa:
        sample_name = str(uuid.uuid4())

        await pa.upload_sample(path, sample_name)
        info = await asyncio.to_thread(read_wav_info, path)
        delay = info.nframes / info.framerate
        while True:
            await pa.play_sample(sample_name)
            await asyncio.sleep(delay)



async def main():
    await asyncio.gather(audio_alert(), visual_alert())

if __name__ == '__main__':
    asyncio.run(main(), debug=1)
