import pytest
import os

from src import NPQuery

@pytest.mark.asyncio
async def test_proxies():
    # Check Webshare Proxies
    query = NPQuery(os.getenv('PROXY_WEBSHARE'))
    await query.check_proxy()
    assert query.proxy_works
    await query.close()

    # # Check PacketStream Proxies
    query = NPQuery(os.getenv('PROXY_PACKETSTREAM'))
    await query.check_proxy()
    assert query.proxy_works
    await query.close()
