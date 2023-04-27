#
#     ___ _ _            _        ___      _        _                    
#    / __\ (_) ___ _ __ | |_     /   \__ _| |_ __ _| |__   __ _ ___  ___ 
#   / /  | | |/ _ \ '_ \| __|   / /\ / _` | __/ _` | '_ \ / _` / __|/ _ \
#  / /___| | |  __/ | | | |_   / /_// (_| | || (_| | |_) | (_| \__ \  __/
#  \____/|_|_|\___|_| |_|\__| /___,' \__,_|\__\__,_|_.__/ \__,_|___/\___|
#                                                                        

import os
import asyncio
import asyncpg

from .db_activities import NPClientActivityDB, NPActivityInfoDB
from ..db import NPDB

class NPClientDB(NPDB):
    def __init__(self, host=None):
        super().__init__(host, table_name='clients')
        self.client_activity_db = NPClientActivityDB()
        self.activity_info_db = NPActivityInfoDB()
    
    async def init(self):
        await NPDB.init(self)
        await self.client_activity_db.init()
        await self.activity_info_db.init()
    
    async def close(self):
        await NPDB.close(self)
        await self.client_activity_db.close()
        await self.activity_info_db.close()
    
    # Creates postgres table for proxies
    async def create_table(self):
        async with self.pool.acquire() as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS clients(
                    id serial PRIMARY KEY,
                    username text UNIQUE DEFAULT '',
                    password text DEFAULT '',
                    email text DEFAULT '',
                    cookie text DEFAULT '',
                    np integer DEFAULT 0,
                    client_type text DEFAULT 'worker',
                    is_registered boolean DEFAULT false,
                    is_activated boolean DEFAULT false,
                    is_limited boolean DEFAULT false,
                    created_at timestamp with time zone DEFAULT NOW(),
                    updated_at timestamp with time zone DEFAULT NOW()
                );
            ''')
    
    # Alters table instead of deleting
    async def alter_table(self):
        async with self.pool.acquire() as conn:
            await conn.execute('''
                ALTER TABLE clients 
                ADD COLUMN client_type text DEFAULT 'worker';
            ''')
    
    # Adds proxy to table
    async def add_account(self,
                          username:str,
                          password:str,
                          email:str,
                          cookie:str=None,
                          np:int=None,
                          is_registered:bool=False,
                          is_activated:bool=False):
        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO clients (username, password, email, cookie, np, is_registered, is_activated)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT (username) DO NOTHING;
            ''', username, password, email, cookie, np, is_registered, is_activated)
        
        await self.client_activity_db.add_account(username)

    # Adds proxy to table
    async def update(self, client):
        cookie = await client.query.export_cookies()
        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO clients (username, password, email, cookie, np, is_registered, is_activated)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT (username) DO NOTHING;
            ''', client.username, client.password, client.email, cookie, client.np, client.is_registered, client.is_activated)
    
    # Gets all clients
    async def get_all(self):
        async with self.pool.acquire() as conn:
            return await conn.fetch('''
                SELECT * FROM clients;
            ''')
    
    # Gets activated clients
    async def get_activated(self, n: int=None):
        async with self.pool.acquire() as conn:
            if n is not None:
                return await conn.fetch('''
                    SELECT * FROM clients
                    WHERE is_registered = true AND is_activated = true
                    LIMIT $1;
                ''', n)
            return await conn.fetch('''
                SELECT * FROM clients
                WHERE is_registered = true AND is_activated = true;
            ''')
    
    # Gets accounts older than 24 hours
    async def get_old_accounts(self, n: int=None):
        async with self.pool.acquire() as conn:
            if n is not None:
                return await conn.fetch('''
                    SELECT * FROM clients 
                    WHERE is_registered = true 
                    AND is_activated = true 
                    AND created_at < NOW() - interval '24 hours'
                    LIMIT $1;
                ''', n)
            return await conn.fetch('''
                SELECT * FROM clients 
                WHERE is_registered = true 
                AND is_activated = true 
                AND created_at < NOW() - interval '24 hours';
            ''')
    
    # Gets activated clients
    async def get_rich(self, cutoff: int=50000):
        async with self.pool.acquire() as conn:
            return await conn.fetch('''
                SELECT * FROM clients
                WHERE is_registered = true AND is_activated = true AND np > $1;
            ''', cutoff)
    
    # Updates NP to current amount
    async def update_np(self, username:str, new_np:int):
        async with self.pool.acquire() as conn:
            await conn.execute('''
                UPDATE clients
                SET np = $2
                WHERE username = $1;
            ''', username, new_np)