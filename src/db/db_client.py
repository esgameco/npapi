#
#     ___ _ _            _        ___      _        _                    
#    / __\ (_) ___ _ __ | |_     /   \__ _| |_ __ _| |__   __ _ ___  ___ 
#   / /  | | |/ _ \ '_ \| __|   / /\ / _` | __/ _` | '_ \ / _` / __|/ _ \
#  / /___| | |  __/ | | | |_   / /_// (_| | || (_| | |_) | (_| \__ \  __/
#  \____/|_|_|\___|_| |_|\__| /___,' \__,_|\__\__,_|_.__/ \__,_|___/\___|
#                                                                        

import time

from .db_default import NPDefaultDB

class NPClientDB(NPDefaultDB):
    """
    username: str (PRIMARY)
    password: str
    email: str
    cookie: str
    np: int
    client_type: str
    is_registered: bool
    is_activated: bool
    is_locked: bool
    last_daily_at: time
    """
    def __init__(self, db):
        super().__init__(db, table_name='clients')
    
    def add(self, val: dict) -> dict:
        return self._add(val, {
            'username': '',
            'password': '',
            'email': '',
            'cookie': '',
            'np': -1,
            'client_type': 'worker',
            'is_registered': False,
            'is_activated': False,
            'is_locked': False,
            'last_daily_at': 0
        }, 'username')

    def get_activated(self):
        return self._get_on_func(lambda n: n['is_registered'] and 
                                           n['is_activated'] and 
                                           not n['is_locked'])
    
    def get_old(self):
        return self._get_on_func(lambda n: n['is_registered'] and 
                                           n['is_activated'] and 
                                           not n['is_locked'] and 
                                           time.time() - n['created_at'] > 86400)
    
    def get_rich(self, cutoff: int=50000):
        return self._get_on_func(lambda n: n['is_registered'] and 
                                           n['is_activated'] and 
                                           not n['is_locked'] and 
                                           time.time() - n['created_at'] > 86400 and 
                                           n['np'] > cutoff)
    
    def get_daily(self):
        return self._get_on_func(lambda n: n['is_registered'] and 
                                           n['is_activated'] and 
                                           not n['is_locked'] and 
                                           time.time() - n['last_daily_at'] > 86400)