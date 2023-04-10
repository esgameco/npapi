import httpx

from fake_useragent import UserAgent

class NPQuery:
    def __init__(self, proxy=None, max_tries=3):
        self.client = httpx.AsyncClient(proxies=None if proxy is None else proxy.pstr)
        self.proxy = proxy
        self.default_headers = self._generate_default_headers()
        self._MAX_TRIES = max_tries
    
    # Generates default headers
    def _generate_default_headers(self):
        ua = UserAgent()
        return {
            'User-Agent': ua.chrome
        }
    
    # Checks whether a cookie is valid or not
    async def check_cookies(self, cookies):
        return None
    
    # Sends GET request (hands control to user)
    async def get(self, url, cookies=None, query_headers=None, params=None):
        headers = self.default_headers.copy()
        if query_headers:
            headers.update(query_headers)

        for i in range(self._MAX_TRIES):
            try:
                return await self.client.get(url, cookies=cookies, headers=headers, params=params)
            except Exception:
                pass
        return None

    # Sends POST request (hands control to user)
    async def post(self, url, data=None, cookies=None, query_headers=None):
        headers = self.default_headers.copy()
        if query_headers:
            headers.update(query_headers)
        
        for i in range(self._MAX_TRIES):
            try:
                return await self.client.post(url, data=data, cookies=cookies, headers=headers)
            except Exception:
                pass
        return None

    async def close(self):
        await self.client.aclose()