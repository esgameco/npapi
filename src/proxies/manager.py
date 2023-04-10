import httpx
import random
import asyncio

from . import NPProxyDB

class NPProxyManager:
    def __init__(self):
        self.services = []
        self.proxies = []
        self.db = NPProxyDB()
    
    async def init(self):
        await self.db.init()
    
    async def init_testing(self):
        await self.init()
        await self.db.delete_table('proxies')
        await self.db.create_table()
    
    async def validate_proxy(self, proxy_str):
        url = 'https://ipv4.icanhazip.com'
        async with httpx.AsyncClient(proxies=httpx.Proxy(proxy_str)) as client:
            res = await client.get(url, timeout=2.0)
        return res.status_code == 200
    
    async def validate_np(self, proxy_str):
        url = 'https://www.neopets.com/signup/index.phtml'
        async with httpx.AsyncClient(proxies=httpx.Proxy(proxy_str)) as client:
            res = await client.post(url, timeout=2.0)
        return len(res.cookies) > 3
    
    # List[str]
    async def test_proxies(self, proxy_list, source, verbose=False):
        for proxy in proxy_list:
            try:
                valid = await self.validate_proxy(proxy)
                valid_np = await self.validate_np(proxy)
                if valid and valid_np:
                    if verbose:
                        print('Proxy added: ', proxy)
                    await self.db.add_proxy(proxy, valid, valid_np, source, 0)
            except Exception as e:
                if verbose:
                    print(e)
    
    async def test_proxy(self, proxy, source, verbose=False):
        try:
            valid = await self.validate_proxy(proxy)
            valid_np = await self.validate_np(proxy)
            if valid and valid_np:
                if verbose:
                    print('Proxy added: ', proxy)
                await self.db.add_proxy(proxy, valid, valid_np, source, 0)
        except Exception as e:
            if verbose:
                print(e)

    # List[str]
    async def test_proxies_fast(self, proxy_list, source, verbose=False):
        print(f'{len(proxy_list)} proxies: ')
        group_amt = 200
        for i in range(int(len(proxy_list)/group_amt)+1):
            print(f'Proxies {i*group_amt}-{(i+1)*group_amt}')
            tasks = []
            for j in range(i*group_amt, (i+1)*group_amt if (i+1)*group_amt < len(proxy_list)-1 else len(proxy_list)-1):
                tasks.append(self.test_proxy(proxy_list[j], source, verbose=verbose))
            await asyncio.gather(*tasks)
        
    # Pulls proxies from database and adds to proxy list
    async def populate_proxies(self):
        proxies = await self.db.get_working_proxies()
        for proxy in proxies:
            self.proxies.append(proxy)
    
    async def get_random(self):
        return random.choice(self.proxies)
    
    async def report_proxy(self, pstr):
        self.db.report_proxy(pstr)