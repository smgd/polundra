from decimal import Decimal
from pathlib import Path
from typing import Type, Any


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


class ScreenBrightness:
    maximal = FileProperty(FileVar('/sys/class/backlight/intel_backlight/max_brightness', int))
    current = FileProperty(FileVar('/sys/class/backlight/intel_backlight/brightness', int))

    @property
    def value(self) -> Decimal:
        return Decimal(self.current) / Decimal(self.maximal)

    @value.setter
    def value(self, v) -> None:
        self.current = int(v * self.maximal)
