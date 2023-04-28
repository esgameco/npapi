#     ___ _ _            _   
#    / __\ (_) ___ _ __ | |_ 
#   / /  | | |/ _ \ '_ \| __|
#  / /___| | |  __/ | | | |_ 
#  \____/|_|_|\___|_| |_|\__|
#                          

import logging
import os
import hashlib
import json
import functools
import re
import time
import asyncio
import aiohttp
import random

from http.cookies import SimpleCookie, Morsel
from typing import Optional

from ..query import NPQuery
from ..exceptions import *
from ..helpers import retry_decorator, NPHelpers

class NPClient:
    def __init__(self, 
                 username: str=None, 
                 password: str=None, 
                 email: str=None,
                 cookie=None, 
                 np: int=None,
                 is_registered: bool=False,
                 is_activated: bool=False,
                 is_locked: bool=False,
                 client_type: str=None,
                 last_daily_at: float=None):
        self.username = username
        self.password = password
        self.email = email
        self.cookie = cookie
        self.np = np
        self.is_registered = is_registered
        self.is_activated = is_activated
        self.is_locked = is_locked
        self.client_type = client_type
        self.last_daily_at = last_daily_at
    
    def _to_dict(self):
        return {
            'username': self.username,
            'password': self.password,
            'email': self.email,
            'cookie': self.cookie,
            'np': self.np,
            'is_registered': self.is_registered,
            'is_activated': self.is_activated,
            'is_locked': self.is_locked,
            'client_type': self.client_type,
            'last_daily_at': self.last_daily_at,
        }
    
    @staticmethod
    def _from_dict(val: dict):
        return NPClient(username=val['username'],
                        password=val['password'],
                        email=val['email'],
                        cookie=val['cookie'],
                        np=val['np'],
                        is_registered=val['is_registered'],
                        is_activated=val['is_activated'],
                        is_locked=val['is_locked'],
                        client_type=val['client_type'],
                        last_daily_at=val['last_daily_at'])
