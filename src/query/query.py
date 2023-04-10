import httpx

from fake_useragent import UserAgent

class NPQuery:
    def __init__(self, proxy=None):
        self.client = httpx.AsyncClient(proxies=proxy)
        self.proxy = proxy
        self.proxy_works = False
        self.default_headers = self._generate_default_headers()
        self._MAX_TRIES = 7
    
    # Generates default headers
    def _generate_default_headers(self):
        ua = UserAgent()
        return {
            'User-Agent': ua.chrome
        }
    
    # Checks whether proxy works at all
    async def check_proxy(self):
        url = 'https://ipv4.icanhazip.com'
        res = await self.client.get(url)
        if res.status_code == 200:
            self.proxy_works = True
    
    # Checks whether a cookie is valid or not
    async def check_cookies(self, cookies):
        return None
    
    # Sends GET request (hands control to user)
    async def get(self, url, cookies=None, query_headers=None):
        headers = self.default_headers.copy()
        if query_headers:
            headers.update(query_headers)

        for i in range(self._MAX_TRIES):
            try:
                return await self.client.get(url, cookies=cookies, headers=headers)
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