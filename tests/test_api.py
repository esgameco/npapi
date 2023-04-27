#   _____          _       _      ___ _____ 
#  /__   \___  ___| |_    /_\    / _ \\_   \
#    / /\/ _ \/ __| __|  //_\\  / /_)/ / /\/
#   / / |  __/\__ \ |_  /  _  \/ ___/\/ /_  
#   \/   \___||___/\__| \_/ \_/\/   \____/  
#                                           

import pytest
import os
import asyncio
import aiohttp
import pickle
import http
import json

from dotenv import load_dotenv
load_dotenv()

from src import NPAPI

@pytest.mark.asyncio
async def test_api_workspace():
    api = NPAPI()
    await api.init()

    await api.new_workspace(delete_old=False, update_proxies=True, premium_proxies=False)

    await api.close()
