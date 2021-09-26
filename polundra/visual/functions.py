from math import pi, sin


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

def f_scr(v):
    return f(v, amplitude=0.95, offset=0.05)
