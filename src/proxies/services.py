import os
import httpx
import asyncio

from ..query import NPQuery

class NPProxyService:
    def __init__(self):
        self.query = NPQuery()
    
    async def get_new(self):
        pass

    async def get_num_new(self, num, slp=0):
        proxies = []
        for i in range(num):
            proxies.append(await self.get_new())
            await asyncio.sleep(slp)
        return proxies

class NPEphemeralService(NPProxyService):
    def __init__(self):
        super().__init__()

    def format(self, proxy_raw):
        return f'http://{proxy_raw["host"]}:{proxy_raw["port"]}/'

    async def get_new(self):
        res = await self.query.get("https://ephemeral-proxies.p.rapidapi.com/v2/datacenter/proxy", query_headers={
            "X-RapidAPI-Key": os.getenv('API_EPH'),
            "X-RapidAPI-Host": "ephemeral-proxies.p.rapidapi.com"
        })

        data = res.json()
        if data['success']:
            return self.format(data['proxy'])
        return None

# Returned (3) Working Proxies in 10 Seconds
class NPProxyListService(NPProxyService):
    def __init__(self):
        super().__init__()

    def format(self, proxy_raw):
        return f'http://{proxy_raw["ip"]}:{proxy_raw["port"]}/'

    async def get_list(self):
        res = await self.query.get("https://proxy-list2.p.rapidapi.com/proxy/get", query_headers={
            "X-RapidAPI-Key": os.getenv('API_PROXYLIST'),
	        "X-RapidAPI-Host": "proxy-list2.p.rapidapi.com"
        }, params={"type":"http","country":"US","anonymity":"high"})

        data = res.json()
        if data and len(data) > 0:
            return [self.format(x) for x in data]
        return None

# Returned (50) Working Proxies in 40 Seconds
class NPSpysService(NPProxyService):
    def __init__(self):
        super().__init__()
    
    def format(self, proxy_raw):
        c_ind = proxy_raw.find(':')
        sp_ind = proxy_raw.find(' ')
        ip = proxy_raw[:c_ind]
        port = proxy_raw[c_ind+1:sp_ind]
        return f'http://{ip}:{port}/'

    async def get_list(self):
        res = await self.query.get("https://spys.me/proxy.txt")

        data = res.text
        if data and len(data) > 0:
            ind = data.find('Google_passed(+)')
            data = data[ind+20:len(data)-72]
            return [self.format(x) for x in data.split('\n')]
        return None

# Returned (1) Working Proxies in 20 Seconds
class NPGeonodeService(NPProxyService):
    def __init__(self):
        super().__init__()
    
    def format(self, proxy_raw):
        return f'http://{proxy_raw["ip"]}:{proxy_raw["port"]}/'

    async def get_list(self):
        res = await self.query.get("https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc&protocols=http%2Chttps")

        data = res.json()
        if data and len(data) > 0:
            return [self.format(x) for x in data['data']]
        return None

# Returned (150) Working Proxies in 1 Minute
class NPProxyScrapeService(NPProxyService):
    def __init__(self):
        super().__init__()
    
    def format(self, proxy_raw):
        pstr = proxy_raw[:-1]
        return f'http://{pstr}/'

    async def get_list(self):
        res = await self.query.get("https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all")

        data = res.text
        if data and len(data) > 0:
            return [self.format(x) for x in data.split('\n')]
        return None

# Returned (150) Working Proxies in 2.5 Minutes
class NPSpeedXService(NPProxyService):
    def __init__(self):
        super().__init__()
    
    def format(self, proxy_raw):
        return f'http://{proxy_raw}/'
    
    def format_socks5(self, proxy_raw):
        return f'socks5'

    async def get_list(self):
        res = await self.query.get("https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt")

        data = res.text
        if data and len(data) > 0:
            return [self.format(x) for x in data.split('\n')]
        return None
    
    async def get_socks_list(self):
        res = await self.query.get("https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt")

        data = res.text
        if data and len(data) > 0:
            return [self.format_socks5(x) for x in data.split('\n')]
        return None

# Returned (150) Working Proxies in 3 Minutes
class NPJetkaiService(NPProxyService):
    def __init__(self):
        super().__init__()
    
    def format(self, proxy_raw):
        return f'http://{proxy_raw}/'

    async def get_list(self):
        res = await self.query.get("https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies.txt")

        data = res.text
        if data and len(data) > 0:
            return [self.format(x) for x in data.split('\n')]
        return None

class NPProxyMasterService(NPProxyService):
    def __init__(self):
        super().__init__()
    
    def format(self, proxy_raw):
        return f'http://{proxy_raw}/'

    def format_socks5(self, proxy_raw):
        return f'socks5://{proxy_raw}/'

    async def get_list(self):
        res = await self.query.get("https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/http.txt")

        data = res.text
        if data and len(data) > 0:
            return [self.format(x) for x in data.split('\n')]
        return None
    
    async def get_socks5_list(self):
        res = await self.query.get("https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/socks5.txt")

        data = res.text
        if data and len(data) > 0:
            return [self.format_socks5(x) for x in data.split('\n')]
        return None