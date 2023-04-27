"""
   ___                          ___      _        _                    
  / _ \_ __ _____  ___   _     /   \__ _| |_ __ _| |__   __ _ ___  ___ 
 / /_)/ '__/ _ \ \/ / | | |   / /\ / _` | __/ _` | '_ \ / _` / __|/ _ \
/ ___/| | | (_) >  <| |_| |  / /_// (_| | || (_| | |_) | (_| \__ \  __/
\/    |_|  \___/_/\_\\__, | /___,' \__,_|\__\__,_|_.__/ \__,_|___/\___|
                     |___/                                             
"""

import os
import asyncio
import asyncpg

from . import NPDB

class NPProxyDB(NPDB):
    def __init__(self, host=None):
        super().__init__(host, table_name='proxies')
    
    # Creates postgres table for proxies
    async def create_table(self):
        async with self.pool.acquire() as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS proxies(
                    id serial PRIMARY KEY,
                    pstr text UNIQUE DEFAULT '',
                    works boolean DEFAULT false,
                    npworks boolean DEFAULT false,
                    source text DEFAULT '',
                    reports integer DEFAULT 0,
                    created_at timestamp with time zone DEFAULT NOW(),
                    updated_at timestamp with time zone DEFAULT NOW()
                );
            ''')
    
    # Alters table instead of deleting
    async def alter_table(self):
        async with self.pool.acquire() as conn:
            await conn.execute('''
                ALTER TABLE proxies 
                ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
            ''')
    
    # Adds proxy to table
    async def add_proxy(self, proxy_str, works, np_works, source, reports):
        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO proxies (pstr, works, npworks, source, reports)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (pstr) DO UPDATE
                SET works = EXCLUDED.works,
                    npworks = EXCLUDED.npworks,
                    source = EXCLUDED.source,
                    reports = EXCLUDED.reports;
            ''', proxy_str, works, np_works, source, reports)
    
    # Gets all proxies
    async def get_all_proxies(self):
        async with self.pool.acquire() as conn:
            return await conn.fetch('''
                SELECT * FROM proxies;
            ''')
    
    # Gets working np proxies (within 1 hour)
    async def get_working_proxies(self):
        async with self.pool.acquire() as conn: # AND updated_at <= NOW() - INTERVAL '1 hour';
            return await conn.fetch('''
                SELECT * FROM proxies
                WHERE
                    npworks = true
                    AND reports < 10;
            ''')
    
    # Reports proxy
    async def report_proxy(self, pstr):
        async with self.pool.acquire() as conn:
            return await conn.execute('''
                UPDATE proxies
                SET 
                    reports = reports + 1, 
                    updated_at = NOW()
                WHERE pstr = $1;
            ''', pstr)
    
    # Gets working np proxies
    async def get_reports(self, pstr):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow('''
                SELECT * FROM proxies
                WHERE pstr = $1;
            ''', pstr)
