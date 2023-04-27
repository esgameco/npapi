#
#     ___                                                                
#    / _ \_ __ _____  ___   _    /\/\   __ _ _ __   __ _  __ _  ___ _ __ 
#   / /_)/ '__/ _ \ \/ / | | |  /    \ / _` | '_ \ / _` |/ _` |/ _ \ '__|
#  / ___/| | | (_) >  <| |_| | / /\/\ \ (_| | | | | (_| | (_| |  __/ |   
#  \/    |_|  \___/_/\_\\__, | \/    \/\__,_|_| |_|\__,_|\__, |\___|_|   
#                       |___/                            |___/           
#  

import logging
import httpx
import random
import asyncio
import aiohttp

from . import NPProxyDB
from .services import NPProxyServiceManager
from ..client import NPFeatureClient
from ..query import NPQuery

logging.basicConfig(level=Warning)

class NPProxyManager:
    def __init__(self, client_manager=None, proxy:str=None):
        self.services = []
        self.proxies = []
        self.db = NPProxyDB()
        self.proxy_service = NPProxyServiceManager(proxy=proxy)
        self.client_manager = client_manager # Pointer (this class does not own client manager)
    
    async def init(self):
        await self.db.init()
        await self.populate_proxies()
    
    async def init_testing(self):
        await self.init()
        await self.db.delete_table('proxies')
        await self.db.create_table()
    
    async def validate_proxy(self, proxy_str, timeout=10):
        try:
            query = NPQuery(proxy=proxy_str, max_tries=1, timeout=timeout)
            res = await query.get('https://www.neopets.com')
            if res.status == 200:
                return True
        except Exception as e:
            logging.warning(f'(ProxyManager validate_proxy) {e}')
            pass
        return False
    
    async def validate_np(self, proxy_str):
        client = NPFeatureClient(proxy=proxy_str)

        try:
            r = await client.basic_proxy_test()

            if not r:
                raise ValueError('Couldn\'t pass sentience check.')

            user_info = await client.gen.gen_user_info()

            await client.register(**user_info)
            has_auth = await client.check_has_auth()

            if has_auth:
                pet_info = await client.do_create_pet()
                activated = await client.do_activate()
                if pet_info and activated:
                    await self.client_manager.add_account(client)

            return True
        except Exception as e:
            return False
    
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
                    logging.warning(e)
    
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
                logging.warning(e)
    
    async def test_proxy_worker(self, queue, source, verbose):
        while not queue.empty():
            proxy = await queue.get()
            await self.test_proxy(proxy, source, verbose)
            queue.task_done()

    # List[str]
    async def test_proxies_fast(self, proxy_list, source, verbose=False, max_proxies: int=300):
        print(f'{source}: {len(proxy_list)} proxies: ')
        queue = asyncio.Queue()

        for proxy in proxy_list:
            queue.put_nowait(proxy)

        tasks = []
        for i in range(max_proxies):
            tasks.append(self.test_proxy_worker(queue, source, verbose))
        await asyncio.gather(*tasks, return_exceptions=True)

        # for i in range(int(len(proxy_list)/group_amt)+1):
        #     max_proxies = (i+1)*group_amt if (i+1)*group_amt < len(proxy_list)-1 else len(proxy_list)-1
        #     print(f'Proxies {i*group_amt}-{max_proxies} / {len(proxy_list)}')
        #     tasks = []
        #     for j in range(i*group_amt, max_proxies):
        #         tasks.append(self.test_proxy(proxy_list[j], source, verbose=verbose))
        #     await asyncio.gather(*tasks)
    
    # Adds new proxies to DB
    async def get_new_proxies(self, premium:bool=False):
        service_manager = NPProxyServiceManager()

        proxies = await service_manager.get_proxies(premium)

        random.shuffle(proxies)
        await self.test_proxies_fast(proxies, 'random', verbose=True)
        
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
        res = await self.db.get_reports(pstr)

        if res['reports'] >= 5:
            print('Proxy removed.')
            self.proxies.remove(pstr)
    
    async def close(self):
        await self.db.close()