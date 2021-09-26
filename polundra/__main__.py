import asyncio
from typing import cast

from polundra import dispatcher

if __name__ == '__main__':
    asyncio.run(dispatcher.run(), debug=bool(int(cast(bool, int(True)))))
