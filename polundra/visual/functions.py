import math
# from decimal import Decimal
from math import pi, sin
from dataclasses import dataclass, field

# pi2 = math.pi * 2


# @dataclass
# class Vibrator:
#     frequency:  = 1.0
#     minimum: float = 0.0
#     maximum: float = 1.0
#     phase: float = 0.0

#     offset: float = field(init=False)
#     amplitude: float = field(init=False)

#     def __post_init__(self):
#         self.offset = self.minimum + self.maximum / 2
#         self.amplitude = self.maximum - self.minimum

#     def __call__(self, v: float) -> float:
#         return self.offset + self.amplitude * sin(2 * pi * (self.phase + v) / self.frequency)

# def vibrator(v: float, minimum: float) -> float:
#     offset = avg(minimum, maximum)
#     amplitude = maximum - minimum
#     return offset + amplitude * sin(phase + v * 2 * pi / frequency)

def f(
    v: float,
    *,
    offset: float = 0.0,
    amplitude: float = 1.0,
    phase: float = 0.0,
    frequency: float = 1.0,
) -> float:
    return amplitude * (0.5 + offset + 0.5 * sin(2 * pi * (phase + v / frequency)))


def f_kbd(v):
    return f(v, phase=0.25)
    # return 0.05 + math.sin(0.5 * math.pi + 2 * math.pi * v)

def f_scr(v):
    return f(v, amplitude=0.95, offset=0.05)
    # return 0.05 + 0.95 * (0.5 + 0.45 * math.sin(2 * math.pi * v))
