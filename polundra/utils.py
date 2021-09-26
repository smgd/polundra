import time


def itertime():
    return iter(time.monotonic, 0)
