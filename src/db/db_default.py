class NPDefaultDB:
    def __init__(self, db, table_name: str='none'):
        self.db = db
        self.table_name = table_name
    
    def create_table(self):
        self.db.create_table(self.table_name)
    
    def update(self, key: any, value: any):
        self.db.set(key, value, table=self.table_name)
    
    def _update_on_func(self, func, value: any):
        return self.db.set_many(func, value, table=self.table_name)
    
    def get(self, key: any):
        return self.db.get(key, table=self.table_name)
    
    def _get_on_func(self, func):
        return self.db.get_many(func, table=self.table_name)
    
    def get_all(self):
        return self.db.get_all(table=self.table_name)
    
    def remove(self, key: any):
        self.db.remove(key, table=self.table_name)

    def _remove_many(self, func):
        self.db.remove_many(func, table=self.table_name)