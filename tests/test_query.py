"""
 _____          _       ____                       
/__   \___  ___| |_    /___ \_   _  ___ _ __ _   _ 
  / /\/ _ \/ __| __|  //  / / | | |/ _ \ '__| | | |
 / / |  __/\__ \ |_  / \_/ /| |_| |  __/ |  | |_| |
 \/   \___||___/\__| \___,_\ \__,_|\___|_|   \__, |
                                             |___/ 
"""

import pytest
import os

from src import NPQuery

# @pytest.mark.asyncio
# async def test_proxies():
#     # Check Webshare Proxies
#     query = NPQuery(os.getenv('PROXY_WEBSHARE'))
#     await query.check_proxy()
#     assert query.proxy_works
#     await query.close()

#     # # Check PacketStream Proxies
#     query = NPQuery(os.getenv('PROXY_PACKETSTREAM'))
#     await query.check_proxy()
#     assert query.proxy_works
#     await query.close()
