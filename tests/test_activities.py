"""
 _____          _       _        _   _       _ _   _           
/__   \___  ___| |_    /_\   ___| |_(_)_   _(_) |_(_) ___  ___ 
  / /\/ _ \/ __| __|  //_\\ / __| __| \ \ / / | __| |/ _ \/ __|
 / / |  __/\__ \ |_  /  _  \ (__| |_| |\ V /| | |_| |  __/\__ \
 \/   \___||___/\__| \_/ \_/\___|\__|_| \_/ |_|\__|_|\___||___/
 
"""

import pytest
import os
import asyncio
import aiohttp
import pickle
import http
import json

from dotenv import load_dotenv
load_dotenv()

from fake_useragent import UserAgent

from src import NPClient, NPGenerateInfo, PetCreationError, RegisterError

@pytest.mark.asyncio
async def test_rich_slorg():
    gen = NPGenerateInfo()
    
    # Testing
    client = NPClient()
    username = os.getenv('NP_TEST_USERNAME')
    password = os.getenv('NP_TEST_PASSWORD')
    await client.login(username, password)

    js = await client.serialize_cookie_jar(client.query.client.cookie_jar)
    cookies = await client.deserialize_cookie_jar(json.loads(js))

    client_new = NPClient(cookies=cookies)
    
    # await client_new.cookie_test()
    donate_amount = 6
    init_np = await client_new.get_np()
    await client_new.donate(6)
    fin_np = await client_new.get_np()

    assert init_np-fin_np == donate_amount

    # print('test_client_cookie', pre_client.username, pre_client.password)
    print('test_client_cookie', username, password)

    await client.close()