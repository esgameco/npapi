#
#     ____                       
#    /___ \_   _  ___ _ __ _   _ 
#   //  / / | | |/ _ \ '__| | | |
#  / \_/ /| |_| |  __/ |  | |_| |
#  \___,_\ \__,_|\___|_|   \__, |
#                          |___/ 
#

import logging
import httpx
import os
import aiohttp
import json
import asyncio
import random

from aiohttp_socks import ProxyConnector
from http.cookies import SimpleCookie, Morsel
from typing import Optional
from fake_useragent import UserAgent

class NPQuery:
    def __init__(self, 
                 proxy: str=None, 
                 cookies=None, 
                 user_agent=None,
                 max_tries: int=3, 
                 timeout: float=10,
                 proxy_manager=None,
                 base_url=None):
        self.proxy = proxy if proxy is not None else os.getenv('PROXY_WEBSHARE') # TODO change before release
        self.connector = ProxyConnector.from_url(self.proxy)
        self.timeout = aiohttp.ClientTimeout(timeout)
        self.client = aiohttp.ClientSession(timeout=self.timeout, cookie_jar=cookies, base_url=base_url, connector=self.connector)
        self.default_headers = self._generate_default_headers(user_agent)
        self.base_url = base_url
        self._MAX_TRIES = max_tries
        self.reports = 0
        self.proxy_manager = proxy_manager
    
    # Reports proxy. If reports > 5, gets a new proxy
    async def report_proxy(self, max_reports: int=10) -> None:
        """Reports proxy and gets a new proxy if enough reports were made"""
        if self.proxy_manager is not None:
            if self.reports >= max_reports:
                await self.proxy_manager.request_remove(self.proxy)
                await self.get_new_proxy()
            else:
                await self.proxy_manager.report_proxy(self.proxy)
                self.reports += 1

    # Gets new proxy if the current one is broken
    async def get_new_proxy(self) -> None:
        """Replaces current proxy with a new random one in the database"""
        self.proxy = await self.proxy_manager.get_random()
        self.connector = ProxyConnector.from_url(self.proxy)
        await self.client.close()
        self.client = aiohttp.ClientSession(timeout=self.timeout, cookie_jar=self.client.cookie_jar, base_url=self.base_url, connector=self.connector)
        self.reports = 0

    # Generates default headers
    def _generate_default_headers(self, user_agent=None) -> dict:
        """Generates headers"""
        ua = UserAgent()
        return {
            'User-Agent': ua.chrome if not user_agent else user_agent
        }
    
    def get_user_agent(self):
        return self.default_headers['User-Agent']

    # Sends GET request (hands control to user)
    async def get(self, url: str, cookies=None, query_headers: dict=None, params: dict=None, referer: str=None, wait: bool=True) -> Optional[any]:
        """Get Request"""
        headers = self.default_headers.copy()
        if query_headers:
            headers.update(query_headers)
        if referer:
            headers['Referer'] = str(referer)

        for i in range(self._MAX_TRIES):
            if wait:
                await asyncio.sleep(random.random())
            try:
                res = await self.client.get(url, cookies=cookies, headers=headers, params=params) # , proxy=self.proxy
                return res
            except Exception as e:
                logging.warning(e)
        await self.report_proxy()
        return None

    # Sends POST request (hands control to user)
    async def post(self, url: str, data: dict=None, cookies=None, query_headers: dict=None, params: dict=None, referer: str=None, wait: bool=True) -> Optional[any]:
        """Post Request"""
        headers = self.default_headers.copy()
        if query_headers:
            headers.update(query_headers)
        if referer:
            headers['Referer'] = str(referer)
        
        for i in range(self._MAX_TRIES):
            if wait:
                await asyncio.sleep(random.random())
            try:
                return await self.client.post(url, data=data, cookies=cookies, headers=headers, params=params) # , proxy=self.proxy
            except Exception as e:
                logging.warning(e)
        await self.report_proxy()
        return None
    
    # Exports cookies
    async def export_cookies(self):
        """Exports cookies from aiohttp client cookie jar"""
        return await self._serialize_cookie_jar(self.client.cookie_jar)
    
    # Imports cookies in json format
    async def process_cookies(self, cookie_jar: str):
        """Imports cookies in the format that they were exported in"""
        if not cookie_jar:
            return None

        cookies = json.loads(cookie_jar)
        # self.client.cookie_jar = await self._deserialize_cookie_jar(cookies)
        return await self._deserialize_cookie_jar(cookies)
    
    # Serialize the aiohttp CookieJar to a JSON string
    async def _serialize_cookie_jar(self, cookie_jar) -> str:
        cookies_list = [
            {
                "key": cookie.key,
                "value": cookie.value,
                "domain": cookie.get("domain", ""),
                "path": cookie.get("path", ""),
                "expires": cookie.get("expires", ""),
                "secure": cookie.get("secure", False),
                "httponly": cookie.get("httponly", False),
            }
            for cookie in cookie_jar
        ]
        return json.dumps(cookies_list)

    # Deserialize the JSON string to an aiohttp CookieJar
    async def _deserialize_cookie_jar(self, cookies_list):
        cookie_jar = aiohttp.CookieJar()
        # self.client.cookie_jar.clear()
        for cookie_dict in cookies_list:
            morsel = Morsel()
            morsel.set(cookie_dict["key"], cookie_dict["value"], cookie_dict["value"])
            morsel["domain"] = cookie_dict["domain"]
            morsel["path"] = cookie_dict["path"]
            morsel["expires"] = cookie_dict["expires"]
            morsel["secure"] = cookie_dict["secure"]
            morsel["httponly"] = cookie_dict["httponly"]

            # Create a SimpleCookie and add the Morsel to it
            cookie = SimpleCookie()
            cookie[morsel.key] = morsel

            # Add the deserialized cookie to the cookie jar
            cookie_jar.update_cookies(cookie)
            # self.client.cookie_jar.update_cookies(cookie)
        
        return cookie_jar

    async def close(self) -> None:
        """Closes Client"""
        await self.client.close()