import time

from typing import List


class NPDefaultDB:
    def __init__(self, db, table_name: str='none'):
        self.db = db
        self.table_name = table_name
        self._init()

    def _init(self):
        self._create_table()
    
    def _create_table(self):
        self.db.create_table(self.table_name)
    
    def _update(self, key: any, value: any):
        self.db.set(key, value, table=self.table_name)
    
    def _add(self, val: dict, schema: dict, primary_key: str) -> dict:
        schema.update(val)
        schema.update({
            'created_at': time.time(),
            'updated_at': time.time()
        })
        return self._update(schema[primary_key], schema)

    def update(self, key: any, val: dict) -> dict:
        schema = self._get(key)
        if not schema:
            return None
        schema.update({
            'updated_at': time.time()
        })
        schema.update(val)
        self._update(key, schema)
        return schema
    
    def _increment_field(self, key: any, field: any) -> dict:
        val = self._get_value(key, field)
        if not val:
            return None
        self.update(key, {field: val+1})
        return val+1
    
    def _update_on_func(self, func, value: any):
        return self.db.set_many(func, value, table=self.table_name)
    
    def _get(self, key: any) -> dict:
        return self.db.get(key, table=self.table_name)
    
    def _get_value(self, key: any, field: any) -> any:
        obj = self._get(key)
        if not obj or field not in obj:
            return None
        return obj[field]
    
    def _get_on_func(self, func) -> List[dict]:
        return self.db.get_many(func, table=self.table_name)
    
    def _get_all(self) -> List[dict]:
        return self.db.get_all(table=self.table_name)
    
    def _remove(self, key: any):
        self.db.remove(key, table=self.table_name)

    def _remove_many(self, func):
        self.db.remove_many(func, table=self.table_name)