"""
___ _ _            _                                              
/ __\ (_) ___ _ __ | |_    /\/\   __ _ _ __   __ _  __ _  ___ _ __ 
/ /  | | |/ _ \ '_ \| __|  /    \ / _` | '_ \ / _` |/ _` |/ _ \ '__|
/ /___| | |  __/ | | | |_  / /\/\ \ (_| | | | | (_| | (_| |  __/ |   
\____/|_|_|\___|_| |_|\__| \/    \/\__,_|_| |_|\__,_|\__, |\___|_|   
                                                    |___/           
"""

import asyncio
import re

from typing import List

from .db_client import NPClientDB
from .db_activities import NPActivityInfoDB
from ..email import NPEmailManager
from ..proxies import NPProxyManager
from ..client import NPClient, NPFeatureClient
from ..query import NPQuery
from ..helpers import NPHelpers

class NPClientManager:
    def __init__(self, proxy:str=None):
        self.db = NPClientDB()
        self.db_activity = NPActivityInfoDB()
        self.email_manager = NPEmailManager(proxy=proxy)
        self.proxy_manager = NPProxyManager(self, proxy=proxy)
        self.query = NPQuery(proxy=proxy)
    
    async def init(self):
        await self.db.init()
        await self.db_activity.init()
        await self.proxy_manager.init()

    # Adds new proxies and accounts to database
    async def add_proxies(self, premium:bool=False):
        await self.proxy_manager.get_new_proxies(premium)
    
    # Adds account using client information
    async def add_account(self, client):
        cookies = await client.query.export_cookies()
        return await self._add_account(username=client.username,
                                        password=client.password,
                                        email=client.email,
                                        cookie=cookies,
                                        np=client.np,
                                        is_registered=client.is_registered,
                                        is_activated=client.is_activated)
    
    # Default add account method
    async def _add_account(self,
                            username:str,
                            password:str,
                            email:str,
                            cookie:str=None,
                            np:int=None,
                            is_registered:bool=False,
                            is_activated:bool=False):
        return await self.db.add_account(username,
                                        password,
                                        email,
                                        cookie,
                                        np,
                                        is_registered,
                                        is_activated)
    
    # Converts client info into actual client
    async def _info_to_client(self, info):
        cookies = await self.query.process_cookies(info['cookie'])
        proxy = await self.proxy_manager.get_random()
        client = NPFeatureClient(username=info['username'],
                                password=info['password'],
                                id=info['id'],
                                cookies=cookies,
                                is_registered=info['is_registered'],
                                is_activated=info['is_activated'],
                                np=info['np'],
                                proxy=proxy,
                                proxy_manager=self.proxy_manager)
        return client

    async def _get_client_worker(self, client):
        try:
            await client.login(random_wait=True)
            print('Logged in', client.username)
            return client
        except Exception as e:
            print('(_get_client_worker)', e)
            return None
    
    async def _get_clients_cookies(self, clients_info):
        return [await self._info_to_client(x) for x in clients_info if x is not None]

    async def _get_client_login(self, info):
        client = await self._info_to_client(info)
        return await self._get_client_worker(client)

    async def _get_clients_login(self, clients_info):
        tasks = []
        for info in clients_info:
            client = await self._info_to_client(info)
            tasks.append(self._get_client_worker(client))
        res = await asyncio.gather(*tasks)
        return [x for x in res if x is not None]

    # Gets activated accounts
    async def get_activated(self, n:int=1):
        """Gets activated accounts
        
        n: Number of accounts

        Returns List[client]
        """
        return [await self._info_to_client(x) for x in await self.db.get_activated()]
    
    # Gets rich accounts
    async def get_rich(self, cutoff:int=50000):
        """Gets rich accounts
        
        cutoff: Minimum NP to qualify as rich
        
        Returns List[client]
        """
        return [await self._info_to_client(x) for x in await self.db.get_rich()]

    async def _create_account_worker(self, queue, max_acc:int=100, do_dailies:bool=True):
        """Creates accounts while still in queue"""
        clients = []

        for i in range(max_acc):
            if queue.empty():
                return clients

            q = await queue.get()

            try:
                proxy = await self.proxy_manager.get_random()
                client = NPFeatureClient(proxy=proxy, proxy_manager=self.proxy_manager)
                await client.create_account()
                if do_dailies:
                    await client.do_dailies(minim=True)
                clients.append(client)
            except Exception as e:
                print(f'(_create_account_worker) {e}')

            queue.task_done()
        return clients

    async def create_accounts(self, num_accounts: int=1, n: int=20, do_dailies=True):
        """Creates a number of accounts
        
        num_accounts: Number of accounts to create
        n: Account workers

        Returns List[client]
        """
        queue = asyncio.Queue()

        for i in range(num_accounts):
            queue.put_nowait(i)

        tasks = []
        for i in range(n):
            tasks.append(self._create_account_worker(queue, do_dailies=do_dailies))

        res = await asyncio.gather(*tasks, return_exceptions=True)

        clients = []
        for worker_res in res:
            if len(worker_res) > 0:
                clients.extend([x for x in worker_res if x is not None])

        return clients

    async def _daily_worker(self, queue, max_acc:int=100):
        """Creates accounts while still in queue"""
        results = []

        for i in range(max_acc):
            if queue.empty():
                return results

            client = await queue.get()

            try:
                res = await client.do_dailies(minim=True, client_db=self.db)
                results.append(res)
            except Exception as e:
                print(f'(_daily_worker) {e}')

            queue.task_done()
        return results

    async def do_dailies(self, clients=None, n: int=15, minim:bool=False, close:bool=False):
        """Does Dailies for each client
        
        clients: Feature Clients that are activated
        n: Max clients at one time
        """
        if not clients:
            db_res = await self.db.client_activity_db.get_needs_daily()
            clients = await self._get_clients_cookies(db_res)
    
        queue = asyncio.Queue()

        for client in clients:
            queue.put_nowait(client)

        tasks = []
        for i in range(n):
            tasks.append(self._daily_worker(queue))

        res = await asyncio.gather(*tasks, return_exceptions=True)

        results = []
        for worker_res in res:
            if len(worker_res) > 0:
                results.extend([x for x in worker_res if x is not None])
        
        if close:
            for client in clients:
                await client.close()

        return results

    async def do_trade(self, sender, reciever, np:int=0, do_all:bool=False, items:List[str]=None):
        """Does a trade of NP from one client to another"""

        if do_all:
            np = await sender.get_np()
        
        trade_number = await reciever.create_trade()
        offer_number = await sender.offer_trade(trade_number, np, items=items)
        if not offer_number:
            print('Offer not successful')
            return None

        accept_success = await reciever.accept_trade(offer_number)
        if not accept_success:
            print('Offer accept not successful')
            return None
        
        return {
            'np': np,
            'items': items
        }
    
    async def update_activity_info(self, first_time:bool=False):
        """Updates activity info for various activities. Only for activities where answer is site-wide."""
        outdated_tasks = []
        if first_time:
            outdated_tasks = [
                {
                    'task': 'daily_puzzle',
                    'info': '',
                }
            ]
        else:
            outdated_tasks = await self.db_activity.get_outdated()

        for task_info in outdated_tasks:
            if task_info['task'] == 'daily_puzzle':
                res = await self.query.get('https://www.jellyneo.net/?go=dailypuzzle')
                msg = await NPHelpers.get_text(res)
                new_info = re.search(r'<strong class="text-blue">(.*?)</strong>', msg).group(1)
                await self.db_activity.update_info('daily_puzzle', new_info)

    async def close(self):
        await self.query.close()
        await self.db.close()
        await self.email_manager.close()
        await self.proxy_manager.close()