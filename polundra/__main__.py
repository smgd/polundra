import asyncio
from typing import cast

from polundra.dispatcher import run

if __name__ == '__main__':
    asyncio.run(run(), debug=bool(int(cast(bool, int(True)))))
