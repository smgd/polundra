import math
import time
from decimal import Decimal
from pathlib import Path
from typing import Type, Any

import vlc


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

    def __init__(self):
        self._start = int(self.current)

    @property
    def value(self) -> Decimal:
        return Decimal(self.current) / Decimal(self.maximal)

    @value.setter
    def value(self, v) -> None:
        self.current = int(v * self.maximal)

    def restore(self):
        self.current = self._start


class Player:
    def __init__(self, sound_path: str = './siren.mp3'):
        self._player = vlc.MediaPlayer(sound_path)

    def play(self):
        self._player.play()

    def stop(self):
        self._player.stop()


def f(v):
    return 0.05 + 0.95 * (0.5 + 0.45 * math.sin(2 * math.pi * v))


def itertime():
    return iter(time.monotonic, 0)


def main():
    brightness = Brightness()
    player = Player()

    player.play()

    try:
        for v in map(f, itertime()):
            brightness.value = v
            time.sleep(1/60)
    except KeyboardInterrupt:
        brightness.restore()
        player.stop()
        exit()


if __name__ == '__main__':
    main()
