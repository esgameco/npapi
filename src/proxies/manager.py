import httpx
import random
import asyncio

from . import NPProxyDB
from ..client import NPClient, NPGenerateInfo

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
        client = NPClient(proxy=proxy_str)
        gen = NPGenerateInfo()

        await client.register(**gen.gen_user_info())

        return await client.check_has_auth()
    
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
    
    async def test_proxy(self, proxy, source, verbose=False, client_manager=None):
        try:
            valid = await self.validate_proxy(proxy)
            valid_np = await self.validate_np(proxy)
            if valid and valid_np:
                if verbose:
                    print('Proxy added: ', proxy)
                if client_manager is not None:
                    client_manager
                await self.db.add_proxy(proxy, valid, valid_np, source, 0)
        except Exception as e:
            if verbose:
                print(e)

    # List[str]
    async def test_proxies_fast(self, proxy_list, source, verbose=False, client_manager=None):
        print(f'{len(proxy_list)} proxies: ')
        group_amt = 200
        for i in range(int(len(proxy_list)/group_amt)+1):
            print(f'Proxies {i*group_amt}-{(i+1)*group_amt}')
            tasks = []
            for j in range(i*group_amt, (i+1)*group_amt if (i+1)*group_amt < len(proxy_list)-1 else len(proxy_list)-1):
                tasks.append(self.test_proxy(proxy_list[j], source, verbose=verbose, client_manager=client_manager))
            await asyncio.gather(*tasks)
        
    # Pulls proxies from database and adds to proxy list
    async def populate_proxies(self):
        proxies = await self.db.get_working_proxies()
        for proxy in proxies:
            self.proxies.append(proxy['pstr'])
    
    async def get_random(self):
        return random.choice(self.proxies)
    
    async def report_proxy(self, pstr):
        await self.db.report_proxy(pstr)
    
    async def request_remove(self, pstr):
        reports = await self.db.get_reports(pstr)

        if reports > 5:
            self.proxies.remove(pstr)