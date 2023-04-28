#     _        _   _       _ _              ___      _        _                    
#    /_\   ___| |_(_)_   _(_) |_ _   _     /   \__ _| |_ __ _| |__   __ _ ___  ___ 
#   //_\\ / __| __| \ \ / / | __| | | |   / /\ / _` | __/ _` | '_ \ / _` / __|/ _ \
#  /  _  \ (__| |_| |\ V /| | |_| |_| |  / /_// (_| | || (_| | |_) | (_| \__ \  __/
#  \_/ \_/\___|\__|_| \_/ |_|\__|\__, | /___,' \__,_|\__\__,_|_.__/ \__,_|___/\___|
#                                |___/                                             

from .db_default import NPDefaultDB

class NPActivityInfoDB(NPDefaultDB):
    """
    task: str
    info: any
    """
    def __init__(self, db):
        super().__init__(db, table_name='activity_info')

    def add(self, val: dict) -> dict:
        return self._add(val, {
            'task': '',
            'info': None
        }, 'task')