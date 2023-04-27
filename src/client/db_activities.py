#     _        _   _       _ _              ___      _        _                    
#    /_\   ___| |_(_)_   _(_) |_ _   _     /   \__ _| |_ __ _| |__   __ _ ___  ___ 
#   //_\\ / __| __| \ \ / / | __| | | |   / /\ / _` | __/ _` | '_ \ / _` / __|/ _ \
#  /  _  \ (__| |_| |\ V /| | |_| |_| |  / /_// (_| | || (_| | |_) | (_| \__ \  __/
#  \_/ \_/\___|\__|_| \_/ |_|\__|\__, | /___,' \__,_|\__\__,_|_.__/ \__,_|___/\___|
#                                |___/                                             

import os
import asyncio
import asyncpg

from ..db import NPDB

class NPActivityInfoDB(NPDB):
    def __init__(self, host=None):
        super().__init__(host, table_name='activityinfo')
        self._cache = {}
    
    def _get_cache(self, name:str):
        return self._cache[name]
    
    def _get_all_cache(self):
        return self._cache.values()
    
    def _add_cache(self, name:str, value:str):
        self._cache[name] = value
    
    async def create_table(self):
        async with self.pool.acquire() as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS activityinfo(
                    id serial PRIMARY KEY,
                    task text UNIQUE DEFAULT '',
                    info text DEFAULT '',
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT '1900-01-01 00:00:00+00'
                );
            ''')
    
    # Alters table instead of deleting
    async def alter_table(self):
        async with self.pool.acquire() as conn:
            await conn.execute('''
                ALTER TABLE activityinfo 
                ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
            ''')
    
    async def add_info(self, task:str, info:str):
        res = None
        async with self.pool.acquire() as conn:
            res = await conn.execute('''
                INSERT INTO activityinfo (task, info)
                VALUES ($1, $2)
                ON CONFLICT (task) DO NOTHING;
            ''', task, info)
        if res == 'INSERT 0 1':
            self._add_cache(task, info)
            return True
        return False
    
    async def get_all(self):
        async with self.pool.acquire() as conn:
            return await conn.fetch('''
                SELECT * FROM activityinfo;
            ''')
    
    async def get_info(self, task:str):
        async with self.pool.acquire() as conn:
            return await conn.fetchval('''
                SELECT info FROM activityinfo
                WHERE task = $1;
            ''', task)
    
    async def get_outdated(self):
        async with self.pool.acquire() as conn: # WHERE NOW() - updated_at <= INTERVAL '24 hours'; Update every time until I find timings for updates.
            res = await conn.fetch('''
                SELECT * FROM activityinfo;
            ''')
            outp = [dict(x) for x in res]
            return outp
    
    async def update_info(self, task:str, info:str):
        res = None
        async with self.pool.acquire() as conn:
            res = await conn.execute('''
                INSERT INTO activityinfo (task, info)
                VALUES ($1, $2)
                ON CONFLICT (task)
                DO UPDATE SET
                    info = EXCLUDED.info,
                    updated_at = NOW();
            ''', task, info)
        if res == 'INSERT 0 1':
            self._add_cache(task, info)
            return True
        return False

class NPClientActivityDB(NPDB):
    def __init__(self, host=None):
        super().__init__(host, table_name='clientactivities')
    
    # Creates postgres table for proxies
    async def create_table(self):
        async with self.pool.acquire() as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS clientactivities(
                    id serial PRIMARY KEY,
                    username text UNIQUE DEFAULT '',
                    last_daily_at timestamp with time zone DEFAULT '1900-01-01 00:00:00+00',
                    last_trudy_at timestamp with time zone DEFAULT '1900-01-01 00:00:00+00',
                    trudy_success boolean DEFAULT false
                );
            ''')
    
    # Alters table instead of deleting
    async def alter_table(self):
        async with self.pool.acquire() as conn:
            await conn.execute('''
                ALTER TABLE clientactivities 
                ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
            ''')
    
    # Adds proxy to table
    async def add_account(self, username:str):
        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO clientactivities (username)
                VALUES ($1)
                ON CONFLICT (username) DO NOTHING;
            ''', username)
    
    # Gets all clients
    async def get_all(self):
        async with self.pool.acquire() as conn:
            return await conn.fetch('''
                SELECT * FROM clientactivities;
            ''')
    
    # Gets clients that need daily
    async def get_needs_daily(self, get_clients=True):
        async with self.pool.acquire() as conn:
            if not get_clients:
                res = await conn.fetch('''
                    SELECT * FROM clientactivities
                    WHERE NOW() - last_daily_at <= INTERVAL '24 hours';
                ''')
                outp = [dict(x) for x in res]
                return outp # Only gets info
            
            return await conn.fetch('''
                SELECT c.*
                FROM clients c
                JOIN clientactivities ca ON c.username = ca.username
                WHERE ca.last_daily_at < NOW() - INTERVAL '24 hours';
            ''')
        
    async def update(self, username:str, results_dict:dict={}):
        async with self.pool.acquire() as conn:
            await conn.execute('''
                UPDATE clientactivities
                SET last_daily_at = NOW()
                WHERE username = $1;
            ''', username)