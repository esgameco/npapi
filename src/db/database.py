"""
    ___      _        _                    
   /   \__ _| |_ __ _| |__   __ _ ___  ___ 
  / /\ / _` | __/ _` | '_ \ / _` / __|/ _ \
 / /_// (_| | || (_| | |_) | (_| \__ \  __/
/___,' \__,_|\__\__,_|_.__/ \__,_|___/\___|
                                           
"""

import os
import asyncio
import asyncpg

class NPDB:
    def __init__(self, host=None):
        self.host = host if host is not None else os.getenv('DB_STR')
        self.pool = None
    
    # Initializes pool
    async def init(self):
        self.pool = await asyncpg.create_pool(self.host)

    async def check_table_exists(self, table_name):
        async with self.pool.acquire() as conn:
            return await conn.fetchval(f'SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name=\'{table_name}\');')

    async def delete_table(self, table_name):
        async with self.pool.acquire() as conn:
            try:
                await conn.execute(f"DROP TABLE IF EXISTS {table_name};")
            except Exception as e:
                print(f"Error deleting the table '{table_name}': {e}")
