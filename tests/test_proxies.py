import pytest
import os
import asyncio

from dotenv import load_dotenv
load_dotenv()

from src import NPClient, NPGenerateInfo, NPProxyManager, NPProxyDB, NPEphemeralService, NPProxyListService, NPSpysService, NPGeonodeService, NPProxyScrapeService, NPSpeedXService, NPJetkaiService, NPProxyMasterService

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
    await proxy_manager.test_proxies(proxies, 'webshare')
    assert await proxy_manager.db.get_all_proxies() is not None

@pytest.mark.asyncio
async def test_proxy_service_eph(): # Paid
    proxy_manager = NPProxyManager()
    await proxy_manager.init_testing()
    
    service = NPEphemeralService()
    proxies = await service.get_num_new(1)
    await proxy_manager.test_proxies_fast(proxies, 'ephemeral', verbose=True)

@pytest.mark.asyncio
async def test_proxy_service_pl(): # 3 / 10s
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
async def test_proxy_service_ps(): # 150 / 1m
    proxy_manager = NPProxyManager()
    await proxy_manager.init_testing()
    
    service = NPProxyScrapeService()
    proxies = await service.get_list()
    await proxy_manager.test_proxies_fast(proxies, 'proxyscrape', verbose=True)

@pytest.mark.asyncio
async def test_proxy_service_speedx(): # 150 / 2.5m
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