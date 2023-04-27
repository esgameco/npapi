#      ___      _        _                    
#     /   \__ _| |_ __ _| |__   __ _ ___  ___ 
#    / /\ / _` | __/ _` | '_ \ / _` / __|/ _ \
#   / /_// (_| | || (_| | |_) | (_| \__ \  __/
#  /___,' \__,_|\__\__,_|_.__/ \__,_|___/\___|
#                                             

#
# In-memory database
#   Tables are keys in the master dict
#   Export/import to/from mongodb
#

import logging
import os
import asyncio
import asyncpg

class NPDB:
    def __init__(self):
        self._cache = {}
    
    def create_table(self, table_name: str, value: any={}):
        self._cache[table_name] = value

    def set(self, key: any, value: any, table: str):
        self._cache[table][key] = value
    
    def set_many(self, pairs: dict, table: str):
        self._cache[table].update(pairs)
    
    def get(self, key: any, table: str):
        return self._cache[table][key]
    
    def get_many(self, func, table: str):
        return [x for x in self._cache[table].values() if func(x)]
    
    def get_all(self, table: str):
        return self._cache[table].values()
    
    def remove(self, key: any, table: str):
        self._cache[table].pop(key)
    
    def remove_many(self, func, table: str):
        for key in self._cache[table]:
            if func(key):
                self._cache[table][key].pop()