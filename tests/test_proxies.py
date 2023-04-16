"""
 _____          _       ___               _           
/__   \___  ___| |_    / _ \_ __ _____  _(_) ___  ___ 
  / /\/ _ \/ __| __|  / /_)/ '__/ _ \ \/ / |/ _ \/ __|
 / / |  __/\__ \ |_  / ___/| | | (_) >  <| |  __/\__ \
 \/   \___||___/\__| \/    |_|  \___/_/\_\_|\___||___/
                                                      
"""

import pytest
import os
import asyncio

from dotenv import load_dotenv
load_dotenv()

from src import NPClient, NPGenerateInfo, NPProxyManager, NPProxyDB, NPEphemeralService, NPProxyListService, NPSpysService, NPGeonodeService, NPProxyScrapeService, NPSpeedXService, NPJetkaiService, NPProxyMasterService, NPWebshareService
from .test_client import do_activate, do_create_pet, do_register

@pytest.mark.asyncio
async def test_proxy_db_table():
    db = NPProxyDB()
    await db.init()
    
    await db.create_table()
    assert await db.check_table_exists('proxies')

@pytest.mark.asyncio
async def test_proxy_list():
    proxy_manager = NPProxyManager()
    await proxy_manager.init_testing()
    
    proxies = [
        # os.getenv('PROXY_WEBSHARE'),
        'http://216.137.184.253:80/'
    ]
    await proxy_manager.test_proxies(proxies, 'random')
    assert await proxy_manager.db.get_all_proxies() is not None

@pytest.mark.asyncio
async def test_proxy_service_webshare(): # Paid
    proxy_manager = NPProxyManager()
    await proxy_manager.init_testing()
    
    service = NPWebshareService()
    proxies = await service.get_num_new(1)
    await proxy_manager.test_proxies_fast(proxies, 'webshare', verbose=True, add_to_db=True)

@pytest.mark.asyncio
async def test_proxy_service_eph(): # Paid
    proxy_manager = NPProxyManager()
    await proxy_manager.init_testing()
    
    service = NPEphemeralService()
    proxies = await service.get_num_new(1)
    await proxy_manager.test_proxies_fast(proxies, 'ephemeral', verbose=True)

@pytest.mark.asyncio
async def test_proxy_service_pl(): # 3 / 10s                                                                                                                                                                                23
    proxy_manager = NPProxyManager()
    await proxy_manager.init_testing()
    
    service = NPProxyListService()
    proxies = await service.get_list()
    await proxy_manager.test_proxies_fast(proxies, 'proxylist', verbose=True)

@pytest.mark.asyncio
async def test_proxy_service_spys(): # 50 / 40s
    proxy_manager = NPProxyManager()
    await proxy_manager.init_testing()
    
    service = NPSpysService()
    proxies = await service.get_list()
    await proxy_manager.test_proxies_fast(proxies, 'spys', verbose=True)

@pytest.mark.asyncio
async def test_proxy_service_geonode(): # 1 / 20s
    proxy_manager = NPProxyManager()
    await proxy_manager.init_testing()
    
    service = NPGeonodeService()
    proxies = await service.get_list()
    await proxy_manager.test_proxies_fast(proxies, 'geonode', verbose=True)

@pytest.mark.asyncio
async def test_proxy_service_ps(): # 60 / 3m
    proxy_manager = NPProxyManager()
    await proxy_manager.init_testing()
    
    service = NPProxyScrapeService()
    proxies = await service.get_list()
    await proxy_manager.test_proxies_fast(proxies, 'proxyscrape', verbose=True)

@pytest.mark.asyncio
async def test_proxy_service_speedx(): # 70 / 7m
    proxy_manager = NPProxyManager()
    await proxy_manager.init_testing()
    
    service = NPSpeedXService()
    proxies = await service.get_list()
    await proxy_manager.test_proxies_fast(proxies, 'speedx', verbose=True)

@pytest.mark.asyncio
async def test_proxy_service_jetkai(): # 150 / 3m
    proxy_manager = NPProxyManager()
    await proxy_manager.init_testing()
    
    service = NPJetkaiService()
    proxies = await service.get_list()
    await proxy_manager.test_proxies_fast(proxies, 'jetkai', verbose=True)

@pytest.mark.asyncio
async def test_proxy_service_pm(): # 50/8000
    proxy_manager = NPProxyManager()
    await proxy_manager.init_testing()
    
    service = NPProxyMasterService()
    proxies = await service.get_list()
    await proxy_manager.test_proxies_fast(proxies, 'proxymaster', verbose=True)

@pytest.mark.asyncio
async def test_proxy_service_pm_socks(): # 0/x
    proxy_manager = NPProxyManager()
    await proxy_manager.init_testing()
    
    service = NPProxyMasterService()
    proxies = await service.get_socks5_list()
    await proxy_manager.test_proxies_fast(proxies, 'proxymastersocks', verbose=True)

@pytest.mark.asyncio
async def test_proxy_random(): # Gets random proxy and tests it on neopets (requires proxies to be in databases)
    proxy_manager = NPProxyManager()
    await proxy_manager.init()
    
    await proxy_manager.populate_proxies()
    proxy = await proxy_manager.get_random()

    client = NPClient(proxy=proxy)
    gen = NPGenerateInfo()
    user_info = await do_register(client, gen)
    await asyncio.sleep(1)
    await do_create_pet(client, gen)
    await asyncio.sleep(10)
    await client.donate(100)
    assert client.get_np() == 2400
    # await do_activate(client, gen, user_info)

    print(user_info)
