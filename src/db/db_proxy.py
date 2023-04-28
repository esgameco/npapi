#     ___                          ___      _        _                    
#    / _ \_ __ _____  ___   _     /   \__ _| |_ __ _| |__   __ _ ___  ___ 
#   / /_)/ '__/ _ \ \/ / | | |   / /\ / _` | __/ _` | '_ \ / _` / __|/ _ \
#  / ___/| | | (_) >  <| |_| |  / /_// (_| | || (_| | |_) | (_| \__ \  __/
#  \/    |_|  \___/_/\_\\__, | /___,' \__,_|\__\__,_|_.__/ \__,_|___/\___|
#                       |___/                                             

import time

from .db_default import NPDefaultDB

class NPProxyDB(NPDefaultDB):
    """
    pstr: str (PRIMARY)
    works: bool
    reports: int
    """
    def __init__(self, db=None):
        super().__init__(db, table_name='proxies')

    def add(self, val: dict) -> dict:
        return self._add(val, {
            'pstr': '',
            'works': False,
            'reports': 0
        }, 'pstr')

    def get_working_proxies(self):
        return self._get_on_func(lambda n: n['npworks'] and n['reports'] < 10)
    
    def report_proxy(self, pstr) -> int:
        return self._increment_field(pstr, 'reports')
    
    def get_reports(self, pstr):
        return self._get_value(pstr, 'reports')
