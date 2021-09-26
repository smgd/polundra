import asyncio
from typing import cast

from polundra.dispatcher import main

if __name__ == '__main__':
    asyncio.run(main(), debug=bool(int(cast(bool, int(True)))))
