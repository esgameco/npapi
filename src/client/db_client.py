import os
import asyncio
import asyncpg

from ..db import NPDB

class NPClientDB(NPDB):
    def __init__(self, host=None):
        super().__init__(host)
    
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
                    reports integer DEFAULT 0
                );
            ''')
    
    # Adds proxy to table
    async def add_proxy(self, proxy_str, works, np_works, source, reports):
        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO proxies (pstr, works, npworks, source, reports)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (pstr) DO NOTHING;
            ''', proxy_str, works, np_works, source, reports)
    
    # Gets all proxies
    async def get_all_proxies(self):
        async with self.pool.acquire() as conn:
            return await conn.fetch('''
                SELECT * FROM proxies;
            ''')
    
    # Gets working np proxies
    async def get_working_proxies(self):
        async with self.pool.acquire() as conn:
            return await conn.fetch('''
                SELECT * FROM proxies
                WHERE npworks = true AND reports <= 5;
            ''')
    
    # Reports proxy
    async def report_proxy(self, pstr):
        async with self.pool.acquire() as conn:
            return await conn.execute('''
                UPDATE proxies
                SET reports = reports + 1
                WHERE pstr = $1;
            ''', pstr)
    
    # Gets working np proxies
    async def get_reports(self, pstr):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow('''
                SELECT * FROM proxies
                WHERE pstr = $1;
            ''', pstr)
