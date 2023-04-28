#    _____ _                      ___      _        _                    
#    \_   \ |_ ___ _ __ ___      /   \__ _| |_ __ _| |__   __ _ ___  ___ 
#     / /\/ __/ _ \ '_ ` _ \    / /\ / _` | __/ _` | '_ \ / _` / __|/ _ \
#  /\/ /_ | ||  __/ | | | | |  / /_// (_| | || (_| | |_) | (_| \__ \  __/
#  \____/  \__\___|_| |_| |_| /___,' \__,_|\__\__,_|_.__/ \__,_|___/\___|
                                                                      
import os
import asyncio
import asyncpg

from .db_default import NPDefaultDB

class NPItemDB(NPDefaultDB):
    """
    name: str
    obj_id: int
    rarity: int
    jellyneo_price: int
    """
    def __init__(self, db=None):
        super().__init__(db, table_name='items')
    
    def add(self, val: dict) -> dict:
        return self._add(val, {
            'name': '',
            'obj_id': -1,
            'rarity': -1,
            'jellyneo_price': -1
        })