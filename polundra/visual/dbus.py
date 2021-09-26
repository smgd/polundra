from decimal import Decimal

import dbus

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


class DBusManager:
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
        self.setter(value)

    @property
    def maximum(self) -> int:
        return self.max_getter()

    @property
    def value(self) -> Decimal:
        return Decimal(self.current) / Decimal(self.maximum)

    @value.setter
    def value(self, v) -> None:
        self.current = int(v * self.maximum)
