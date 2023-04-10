class Proxy:
    def __init__(self, pstr, works, np_works, source, reports, proxy_manager):
        self.proxy_manager = proxy_manager
        self.pstr = pstr
        self.works = works
        self.np_works = np_works
        self.source = source
        self.reports = reports
    
    async def report(self):
        self.proxy_manager.report_proxy()
    
    async def get_new(self):
        new_proxy = self.proxy_manager.get_random()
        