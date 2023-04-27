#  
#     ___                       __                 _               
#    / _ \_ __ _____  ___   _  / _\ ___ _ ____   _(_) ___ ___  ___ 
#   / /_)/ '__/ _ \ \/ / | | | \ \ / _ \ '__\ \ / / |/ __/ _ \/ __|
#  / ___/| | | (_) >  <| |_| | _\ \  __/ |   \ V /| | (_|  __/\__ \
#  \/    |_|  \___/_/\_\\__, | \__/\___|_|    \_/ |_|\___\___||___/
#                       |___/                                      
#  

import os
import httpx
import asyncio
import random

from typing import List

from ..query import NPQuery
from ..helpers import NPHelpers

class NPProxyServiceManager:
    def __init__(self, proxy:str=None) -> None:
        self.proxy = proxy if proxy is not None else os.getenv('PROXY_WEBSHARE') # TODO change before release

    # Gets a list of HTTP ONLY proxies (socks not confirmed to work)
    async def get_proxies(self, paid:bool=False) -> List[str]:
        if paid:
            service = NPWebshareService()
            proxies = await service.get_list()
            await service.close()
            return proxies

        services = [
            NPSpysService(),
            NPProxyScrapeService(),
            NPSpeedXService(),
        ]

        proxies = []
        for service in services:
            proxies.extend(await service.get_list())
            await service.close()
        proxies = list(set(proxies))
        return proxies

class NPProxyService:
    def __init__(self, proxy:str=None):
        self.query = NPQuery(proxy=proxy)
    
    async def get_new(self):
        pass

    async def get_num_new(self, num, slp=0):
        proxies = []
        for i in range(num):
            proxies.append(await self.get_new())
            await asyncio.sleep(slp)
        return proxies

    async def get_list(self):
        pass

    async def close(self):
        await self.query.close()
    
class NPWebshareService(NPProxyService):
    def __init__(self, proxy:str=None):
        super().__init__(proxy)

    def format(self, proxy_raw):
        parts = proxy_raw.split(':')
        if len(parts) < 4:
            return None
        ip = parts[0]
        port = parts[1]
        username = parts[2]
        password = parts[3]
        return f'http://{username}:{password}@{ip}:{port}/'

    async def get_list(self): # Only gets 100. If you have more, you can use pagination.
        res = await self.query.get(os.getenv('PROXY_WEB_LIST'), wait=False)

        data = await res.text()
        if data and len(data) > 0:
            return [self.format(x) for x in data.split('\r\n')]
        return None

class NPEphemeralService(NPProxyService):
    def __init__(self, proxy:str=None):
        super().__init__(proxy)

    def format(self, proxy_raw):
        return f'http://{proxy_raw["host"]}:{proxy_raw["port"]}/'

    async def get_new(self):
        res = await self.query.get("https://ephemeral-proxies.p.rapidapi.com/v2/datacenter/proxy", query_headers={
            "X-RapidAPI-Key": os.getenv('API_EPH'),
            "X-RapidAPI-Host": "ephemeral-proxies.p.rapidapi.com"
        }, wait=False)

        data = await res.json()
        if data['success']:
            return self.format(data['proxy'])
        return None

# Returned (3) Working Proxies in 10 Seconds
class NPProxyListService(NPProxyService):
    def __init__(self, proxy:str=None):
        super().__init__(proxy)

    def format(self, proxy_raw):
        return f'http://{proxy_raw["ip"]}:{proxy_raw["port"]}/'

    async def get_list(self):
        res = await self.query.get("https://proxy-list2.p.rapidapi.com/proxy/get", query_headers={
            "X-RapidAPI-Key": os.getenv('API_PROXYLIST'),
	        "X-RapidAPI-Host": "proxy-list2.p.rapidapi.com"
        }, params={"type":"http","country":"US","anonymity":"high"}, wait=False)

        data = await res.json()
        if data and len(data) > 0:
            return [self.format(x) for x in data]
        return None

# Returned (50) Working Proxies in 40 Seconds
class NPSpysService(NPProxyService):
    def __init__(self, proxy:str=None):
        super().__init__(proxy)
    
    def format(self, proxy_raw):
        c_ind = proxy_raw.find(':')
        sp_ind = proxy_raw.find(' ')
        ip = proxy_raw[:c_ind]
        port = proxy_raw[c_ind+1:sp_ind]
        return f'http://{ip}:{port}/'
    
    def format_socks(self, proxy_raw):
        c_ind = proxy_raw.find(':')
        sp_ind = proxy_raw.find(' ')
        ip = proxy_raw[:c_ind]
        port = proxy_raw[c_ind+1:sp_ind]
        return f'socks5://{ip}:{port}/'

    async def get_all(self):
        proxies = []
        for source in [ await self.get_list(), await self.get_socks() ]:
            proxies.extend(source)
        return proxies

    async def get_list(self):
        res = await self.query.get("https://spys.me/proxy.txt", wait=False)

        data = await res.text()
        if data and len(data) > 0:
            ind = data.find('Google_passed(+)')
            data = data[ind+20:len(data)-72]
            return [self.format(x) for x in data.split('\n')]
        return None

    async def get_socks(self):
        res = await self.query.get("https://spys.me/socks.txt", wait=False)

        data = await res.text()
        if data and len(data) > 0:
            ind = data.find('Google_passed(+)')
            data = data[ind+20:len(data)-72]
            return [self.format_socks(x) for x in data.split('\n')]
        return None

# Returned (1) Working Proxies in 20 Seconds
class NPGeonodeService(NPProxyService):
    def __init__(self, proxy:str=None):
        super().__init__(proxy)
    
    def format(self, proxy_raw):
        return f'http://{proxy_raw["ip"]}:{proxy_raw["port"]}/'

    async def get_list(self):
        res = await self.query.get("https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc&protocols=http%2Chttps", wait=False)

        data = await res.json()
        if data and len(data) > 0:
            return [self.format(x) for x in data['data']]
        return None

# Returned (150) Working Proxies in 1 Minute
class NPProxyScrapeService(NPProxyService):
    def __init__(self, proxy:str=None):
        super().__init__(proxy)
    
    def format(self, proxy_raw):
        pstr = proxy_raw[:-1]
        return f'http://{pstr}/'
    
    def format_socks4(self, proxy_raw):
        pstr = proxy_raw[:-1]
        return f'socks4://{pstr}/'

    def format_socks5(self, proxy_raw):
        pstr = proxy_raw[:-1]
        return f'socks5://{pstr}/'

    async def get_all(self):
        proxies = []
        for source in [ await self.get_list(), await self.get_socks4(), await self.get_socks5() ]:
            proxies.extend(source)
        return proxies

    async def get_list(self):
        res = await self.query.get("https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=1000&country=all&ssl=all&anonymity=all", wait=False)

        data = await res.text()
        if data and len(data) > 0:
            return [self.format(x) for x in data.split('\n')]
        return None

    async def get_socks4(self):
        res = await self.query.get("https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks4&timeout=1000&country=all", wait=False)

        data = await res.text()
        if data and len(data) > 0:
            return [self.format_socks4(x) for x in data.split('\n')]
        return None
    
    async def get_socks5(self):
        res = await self.query.get("https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks5&timeout=1000&country=all", wait=False)

        data = await res.text()
        if data and len(data) > 0:
            return [self.format_socks5(x) for x in data.split('\n')]
        return None

# Returned (150) Working Proxies in 2.5 Minutes
class NPSpeedXService(NPProxyService):
    def __init__(self, proxy:str=None):
        super().__init__(proxy)
    
    def format(self, proxy_raw):
        return f'http://{proxy_raw}/'
    
    def format_socks4(self, proxy_raw):
        return f'socks4://{proxy_raw}/'

    def format_socks5(self, proxy_raw):
        return f'socks5://{proxy_raw}/'

    async def get_all(self):
        all_lists = []
        all_lists.extend(await self.get_list())
        all_lists.extend(await self.get_socks4_list())
        all_lists.extend(await self.get_socks5_list())
        return all_lists

    async def get_list(self):
        res = await self.query.get("https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt", wait=False)

        data = await res.text()
        if data and len(data) > 0:
            return [self.format(x) for x in data.split('\n')]
        return None
    
    async def get_socks4_list(self):
        res = await self.query.get("https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt", wait=False)

        data = await res.text()
        if data and len(data) > 0:
            return [self.format_socks4(x) for x in data.split('\n')]
        return None

    async def get_socks5_list(self):
        res = await self.query.get("https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt", wait=False)

        data = await res.text()
        if data and len(data) > 0:
            return [self.format_socks5(x) for x in data.split('\n')]
        return None

# Returned (150) Working Proxies in 3 Minutes
class NPJetkaiService(NPProxyService):
    def __init__(self, proxy:str=None):
        super().__init__(proxy)
    
    def format(self, proxy_raw):
        return f'http://{proxy_raw}/'

    async def get_list(self):
        res = await self.query.get("https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies.txt", wait=False)

        data = await res.text()
        if data and len(data) > 0:
            return [self.format(x) for x in data.split('\n')]
        return None

class NPProxyMasterService(NPProxyService):
    def __init__(self, proxy:str=None):
        super().__init__(proxy)
    
    def format(self, proxy_raw):
        return f'http://{proxy_raw}/'

    def format_socks4(self, proxy_raw):
        return f'socks4://{proxy_raw}/'

    def format_socks5(self, proxy_raw):
        return f'socks5://{proxy_raw}/'

    async def get_list(self):
        res = await self.query.get("https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/http.txt", wait=False)

        data = await res.text()
        if data and len(data) > 0:
            return [self.format(x) for x in data.split('\n')]
        return None
    
    async def get_socks4_list(self):
        res = await self.query.get("https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/socks4.txt", wait=False)

        data = await res.text()
        if data and len(data) > 0:
            return [self.format_socks4(x) for x in data.split('\n')]
        return None

    async def get_socks5_list(self):
        res = await self.query.get("https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/socks5.txt", wait=False)

        data = await res.text()
        if data and len(data) > 0:
            return [self.format_socks5(x) for x in data.split('\n')]
        return None