import math


def f(v, for_keyboard=False):
    if for_keyboard:
        return 0.05 + math.sin(0.5 * math.pi + 2 * math.pi * v)
    return 0.05 + 0.95 * (0.5 + 0.45 * math.sin(2 * math.pi * v))
