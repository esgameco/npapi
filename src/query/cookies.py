import httpx

class NPCookieJar:
    def __init__(self, text_cookies=None, domain=None):
        self.cookies = httpx.Cookies()
        if text_cookies:
            self.import_from_text(text_cookies, domain)
    
    def import_from_text(self, text, domain):
        txt_cookies = [{'name': x.split('=')[0], 'value': x.split('=')[1]} for x in text.split(';')]

        for c in txt_cookies:
            self.add_cookies(txt_cookies, domain)

    def import_from_response(self, res):
        self.cookies.extract_cookies(res)

    def add_cookies(self, cookies, domain):
        for cookie in cookies:
            self.add_cookie(cookie, domain)

    def add_cookie(self, cookie, domain):
        self.cookies.set(cookie['name'], cookie['value'], domain)
    
    def get_all(self):
        return self.cookies
    
    def get(self, name):
        return self.cookies.get(name)