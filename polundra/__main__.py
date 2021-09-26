import asyncio
from typing import cast

from polundra import dispatcher


def main():
    asyncio.run(dispatcher.run(), debug=bool(int(cast(bool, int(True)))))


if __name__ == '__main__':
    main()
