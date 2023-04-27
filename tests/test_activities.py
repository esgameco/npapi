#   _____          _       _        _   _       _ _   _           
#  /__   \___  ___| |_    /_\   ___| |_(_)_   _(_) |_(_) ___  ___ 
#    / /\/ _ \/ __| __|  //_\\ / __| __| \ \ / / | __| |/ _ \/ __|
#   / / |  __/\__ \ |_  /  _  \ (__| |_| |\ V /| | |_| |  __/\__ \
#   \/   \___||___/\__| \_/ \_/\___|\__|_| \_/ |_|\__|_|\___||___/

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

from src import NPFeatureClient, NPGenerateInfo, PetCreationError, RegisterError, NPProxyManager, NPClientManager

from .test_client import create_account

@pytest.mark.asyncio
async def test_activities():
    client_manager = NPClientManager()
    await client_manager.init()

    clients_raw = await client_manager.db.client_activity_db.get_needs_daily()
    client = await client_manager._info_to_client(clients_raw[0])
    # await client.login()

    res = await client.do_dailies(minim=True, client_db=client_manager.db)

    print('test_activities')

    await client_manager.close()

@pytest.mark.asyncio
async def test_activity_trudy():
    client_manager = NPClientManager()
    await client_manager.init()

    accounts = await client_manager.create_accounts(num_accounts=1, do_dailies=False)
    assert len(accounts) == 1
    client = accounts[0]

    await client.claim_trudy()

    np = await client.get_np()
    assert np > 2500

    await client_manager.close()

@pytest.mark.asyncio
async def test_activity_puzzle():
    client_manager = NPClientManager()
    await client_manager.init()

    await client_manager.update_activity_info()

    accounts = await client_manager.create_accounts(num_accounts=1, do_dailies=False)
    assert len(accounts) == 1
    client = accounts[0]

    await client.daily_puzzle()

    np = await client.get_np()
    assert np > 2500

    await client_manager.close()

@pytest.mark.asyncio
async def test_activity_rich_slorg():
    gen = NPGenerateInfo()
    
    # Testing
    client = NPFeatureClient()
    username = os.getenv('NP_TEST_USERNAME')
    password = os.getenv('NP_TEST_PASSWORD')
    await client.login(username, password)

    js = await client.serialize_cookie_jar(client.query.client.cookie_jar)
    cookies = await client.deserialize_cookie_jar(json.loads(js))

    client_new = NPFeatureClient(cookies=cookies)
    
    # await client_new.cookie_test()
    donate_amount = 6
    init_np = await client_new.get_np()
    await client_new.donate(6)
    fin_np = await client_new.get_np()

    assert init_np-fin_np == donate_amount

    # print('test_client_cookie', pre_client.username, pre_client.password)
    print('test_client_cookie', username, password)

    await client.close()