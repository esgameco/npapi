import asyncio

from src import NPAPI

if __name__ == '__main__':
    api = NPAPI()

    asyncio.run(api.donate_run())