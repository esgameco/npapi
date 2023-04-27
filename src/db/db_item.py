#    _____ _                      ___      _        _                    
#    \_   \ |_ ___ _ __ ___      /   \__ _| |_ __ _| |__   __ _ ___  ___ 
#     / /\/ __/ _ \ '_ ` _ \    / /\ / _` | __/ _` | '_ \ / _` / __|/ _ \
#  /\/ /_ | ||  __/ | | | | |  / /_// (_| | || (_| | |_) | (_| \__ \  __/
#  \____/  \__\___|_| |_| |_| /___,' \__,_|\__\__,_|_.__/ \__,_|___/\___|
                                                                      
import os
import asyncio
import asyncpg

from . import NPDB

class NPItemDB(NPDB):
    def __init__(self, host=None):
        """
        Cache is indexed by obj_id. Fastest way to access is through obj_id.
        Each object in the cache contains all data, including obj_id.
        """
        super().__init__(host, table_name='items')
        self._cache = {}
        self._is_populated = False

    def _get_cache(self, name:str=None, obj_id:int=None):
        """Gets cached data. Access through obj_id is significantly faster than through name."""
        if obj_id:
            try:
                return self._cache[obj_id]
            except Exception as e:
                print(f'(_get_cache) obj_id cache miss: {e}')
                return None
        elif name:
            try:
                for obj in self._cache.values():
                    if obj.name == name:
                        return obj
            except Exception as e:
                print(f'(_get_cache) name cache miss: {e}')
                return None
        return None

    def _get_all_cache(self):
        """Returns all values in the cache"""
        return self._cache.values()

    def _add_cache(self, res) -> bool:
        """Adds or updates a value to the cache"""
        if not res['obj_id']:
            return False
        res_obj = dict(res)
        try:
            self._cache[res_obj['obj_id']] = res_obj.copy()
            return True
        except Exception as e:
            print(f'(_add_cache) cache add failed: {e}')
        return False
    
    def _add_cache_multiple(self, res) -> bool:
        for obj in res:
            self._add_cache(obj)
        return True

    async def create_table(self):
        async with self.pool.acquire() as conn:
            return await conn.execute('''
                CREATE TABLE IF NOT EXISTS items(
                    id serial PRIMARY KEY,
                    name text UNIQUE DEFAULT '',
                    obj_id integer UNIQUE DEFAULT 0,
                    jellyneo_price integer DEFAULT 0,
                    rarity text DEFAULT 0,
                    interested boolean DEFAULT false,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT '1900-01-01 00:00:00+00'
                );
            ''')
    
    # Alters table instead of deleting
    async def alter_table(self):
        async with self.pool.acquire() as conn:
            return await conn.execute('''
                ALTER TABLE items 
                ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
            ''')
    
    async def add_item(self, name: str, obj_id: int, jellyneo_price: int, rarity: str, interested: bool=False) -> bool:
        """Adds item to database and cache"""
        res = None
        async with self.pool.acquire() as conn:
            res = await conn.execute('''
                INSERT INTO items (name, obj_id, jellyneo_price, rarity, interested)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (name) DO NOTHING
                ON CONFLICT (obj_id) DO NOTHING;
            ''', name, obj_id, jellyneo_price, rarity, interested)
        if res == 'INSERT 0 1':
            self._add_cache({
                'name': name,
                'obj_id': obj_id,
                'jellyneo_price': jellyneo_price,
                'rarity': rarity,
                'interested': interested
            })
            return True
        return False
    
    async def populate_cache(self):
        await self.get_all()
    
    async def get_all(self, query: str=None, do_all: bool=True):
        if not query:
            query = '''
                SELECT * FROM items;
            '''
            
        res = None
        if self._is_populated:
            return self._get_all_cache()
        async with self.pool.acquire() as conn:
            res = await conn.fetch(query)
        if res is not None:
            self._add_cache_multiple(res)
            if do_all:
                self._is_populated = True
        return res
    
    async def get_item(self, name: str=None, obj_id: int=None, query: str=None):
        if not query:
            query = '''
                SELECT * FROM items
                WHERE replace_me = $1;
            '''

        res = self._get_cache(name, obj_id)
        if res is not None:
            return res
        async with self.pool.acquire() as conn:
            if name:
                res = await conn.fetchval(query.replace('replace_me', 'name'), name)
            if obj_id:
                res = await conn.fetchval(query.replace('replace_me', 'obj_id'), obj_id)
        if res is not None:
            self._add_cache(res)
        return res
    
    async def get_outdated(self):
        return await self.get_all('''
                SELECT * FROM items
                WHERE interested = true AND NOW() - updated_at <= INTERVAL '24 hours';
            ''', do_all=False)
    
    async def update_item_price(self, name: str=None, obj_id: int=None, new_price: int=0):
        query = '''
            UPDATE items
            SET 
                jellyneo_price = $2, 
                updated_at = NOW()
            WHERE replace_me = $1;
        '''

        async with self.pool.acquire() as conn:
            if name:
                return await conn.execute(query.replace('replace_me', name), name, new_price)
            if obj_id:
                return await conn.execute(query.replace('replace_me', obj_id), obj_id, new_price)
        return None

# TODO
class NPWizardDB(NPDB):
    def __init__(self, host=None):
        super().__init__(host, table_name='items_wizard')
    
    async def create_table(self):
        async with self.pool.acquire() as conn:
            return await conn.execute('''
                CREATE TABLE IF NOT EXISTS items(
                    id serial PRIMARY KEY,
                    obj_id integer UNIQUE DEFAULT 0,
                    jellyneo_price integer DEFAULT 0,
                    rarity text DEFAULT 0,
                    interested boolean DEFAULT false,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT '1900-01-01 00:00:00+00'
                );
            ''')
    
    # Alters table instead of deleting
    async def alter_table(self):
        async with self.pool.acquire() as conn:
            return await conn.execute('''
                ALTER TABLE items 
                ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
            ''')
    
    async def add_item(self, name: str, obj_id: int, jellyneo_price: int, rarity: str, interested: bool=False):
        async with self.pool.acquire() as conn:
            return await conn.execute('''
                INSERT INTO items (name, obj_id, jellyneo_price, rarity, interested)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (name) DO NOTHING
                ON CONFLICT (obj_id) DO NOTHING;
            ''', name, obj_id, jellyneo_price, rarity, interested)
    
    async def get_all(self):
        async with self.pool.acquire() as conn:
            return await conn.fetch('''
                SELECT * FROM items;
            ''')
    
    async def get_item(self, name: str=None, obj_id: int=None):
        if name:
            async with self.pool.acquire() as conn:
                return await conn.fetchval('''
                    SELECT * FROM items
                    WHERE name = $1;
                ''', name)
        if obj_id:
            async with self.pool.acquire() as conn:
                return await conn.fetchval('''
                    SELECT * FROM items
                    WHERE obj_id = $1;
                ''', obj_id)
        return None
    
    async def get_outdated(self):
        async with self.pool.acquire() as conn:
            return await conn.fetch('''
                SELECT * FROM items
                WHERE interested = true AND NOW() - updated_at <= INTERVAL '24 hours';
            ''')
    
    async def update_item_price(self, name: str=None, obj_id: int=None, new_price: int=0):
        if name:
            async with self.pool.acquire() as conn:
                return await conn.execute('''
                    UPDATE proxies
                    SET 
                        jellyneo_price = $2, 
                        updated_at = NOW()
                    WHERE name = $1;
                ''', name, new_price)
        if obj_id:
            async with self.pool.acquire() as conn:
                return await conn.execute('''
                    UPDATE proxies
                    SET 
                        jellyneo_price = $2, 
                        updated_at = NOW()
                    WHERE obj_id = $1;
                ''', name, new_price)
        return None