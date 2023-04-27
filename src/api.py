#     _       ___    _____ 
#    /_\     / _ \   \_   \
#   //_\\   / /_)/    / /\/
#  /  _  \ / ___/  /\/ /_  
#  \_/ \_/ \/      \____/  
#                          

import logging
import asyncio
import random
from dotenv import load_dotenv
load_dotenv()

from .client import NPClientManager, NPClientDB, NPActivityInfoDB, NPClientActivityDB
from .proxies import NPProxyDB

class NPAPI:
    def __init__(self):
        self.client_manager = NPClientManager()
    
    async def init(self):
        """ Initializes databases and query objects. ***RUN THIS BEFORE ANYTHING ELSE *** """
        await self.client_manager.init()
    
    async def _get_dbs(self):
        return [
            NPClientDB(),
            NPProxyDB(),
            NPActivityInfoDB(),
            NPClientActivityDB()
        ]

    async def _reset_db(self):
        """ Deletes database data and adds again """
        dbs = await self._get_dbs()
        for db in dbs:
            await db.init()
            await db.delete_table(db.table_name)
            await db.create_table()
            await db.close()
    
    async def new_workspace(self, delete_old=False, update_proxies:bool=True, premium_proxies=False):
        """ Starts a new workspace, which entails the following:

        - Deletes existing data (if specified)
        - Updates proxies
        - Updates activity data
        """
        if delete_old:
            await self._reset_db()

        if update_proxies:
            await self.update_proxies(premium=premium_proxies)

        await self.client_manager.update_activity_info(first_time=True)
        
        await self.do_dailies(minim=True)

    async def update_proxies(self, premium:bool=False):
        """ Adds new usable proxies to the database, specifically:

        - Creates an account
        -- If the account was created successfully, add proxy to db
        """
        await self.client_manager.add_proxies(premium=premium)
    
    async def do_dailies(self, minim:bool=False):
        """ Does dailies for each client that needs to do dailies"""
        await self.client_manager.do_dailies(minim=minim)

    async def close(self):
        await self.client_manager.close()