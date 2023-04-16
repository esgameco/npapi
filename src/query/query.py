"""
   ____                       
  /___ \_   _  ___ _ __ _   _ 
 //  / / | | |/ _ \ '__| | | |
/ \_/ /| |_| |  __/ |  | |_| |
\___,_\ \__,_|\___|_|   \__, |
                        |___/ 
"""

import httpx
import os
import aiohttp

from typing import Optional
from fake_useragent import UserAgent

class NPQuery:
    def __init__(self, 
                 proxy: str=None, 
                 cookies=None, 
                 user_agent=None,
                 max_tries: int=3, 
                 proxy_manager=None,
                 base_url=None):
        self.proxy = proxy if proxy is not None else os.getenv('PROXY_WEBSHARE')
        self.timeout = aiohttp.ClientTimeout(5)
        self.client = aiohttp.ClientSession(timeout=self.timeout, cookie_jar=cookies, base_url=base_url)
        self.default_headers = self._generate_default_headers(user_agent)
        self._MAX_TRIES = max_tries
        self.reports = 0
        self.proxy_manager = proxy_manager
    
    # Reports proxy. If reports > 5, gets a new proxy
    async def report_proxy(self) -> None:
        """Reports proxy and gets a new proxy if enough reports were made"""
        if self.proxy_manager is not None:
            if self.reports > 5:
                await self.proxy_manager.request_remove(self.proxy.url)
                await self.get_new_proxy()
            else:
                await self.proxy_manager.report_proxy(self.proxy.url)
                self.reports += 1

    # Gets new proxy if the current one is broken
    async def get_new_proxy(self) -> None:
        """Replaces current proxy with a new random one in the database"""
        self.proxy = await self.proxy_manager.get_random()
        self.client = httpx.AsyncClient(proxies=self.proxy)
    
    # Generates default headers
    def _generate_default_headers(self, user_agent=None) -> dict:
        """Generates headers"""
        ua = UserAgent()
        return {
            'User-Agent': ua.chrome if user_agent is None else user_agent
        }
    
    def get_user_agent(self):
        return self.default_headers['User-Agent']

    # Sends GET request (hands control to user)
    async def get(self, url: str, cookies=None, query_headers: dict=None, params: dict=None) -> Optional[any]:
        """Get Request"""
        headers = self.default_headers.copy()
        if query_headers:
            headers.update(query_headers)

        for i in range(self._MAX_TRIES):
            try:
                return await self.client.get(url, cookies=cookies, headers=headers, params=params, proxy=self.proxy)
            except Exception as e:
                print(e)
        await self.report_proxy()
        return None

    # Sends POST request (hands control to user)
    async def post(self, url: str, data: dict=None, cookies=None, query_headers: dict=None, params: dict=None) -> Optional[any]:
        """Post Request"""
        headers = self.default_headers.copy()
        if query_headers:
            headers.update(query_headers)
        
        for i in range(self._MAX_TRIES):
            try:
                return await self.client.post(url, data=data, cookies=cookies, headers=headers, params=params, proxy=self.proxy)
            except Exception as e:
                print(e)
        await self.report_proxy()
        return None

    async def close(self) -> None:
        """Closes Client"""
        await self.client.close()