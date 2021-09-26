import asyncio
import subprocess

import pulsectl


class Pulse(pulsectl.Pulse):
    async def __aenter__(self):
        await asyncio.to_thread(self.__enter__)
        return self

    async def __aexit__(self, *exc_info):
        await asyncio.to_thread(self.__exit__, *exc_info)

    async def upload_sample(self, filename, name):
        return await asyncio.to_thread(self._upload_sample, filename, name)

    @staticmethod
    def _upload_sample(filename, name):
        with subprocess.Popen(['pactl', 'upload-sample', filename, name]) as proc:
            proc.wait()

    async def play_sample(self, name, *__, **___):
        return await asyncio.to_thread(super().play_sample, name, *__, **___)
