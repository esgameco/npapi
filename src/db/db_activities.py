#     _        _   _       _ _              ___      _        _                    
#    /_\   ___| |_(_)_   _(_) |_ _   _     /   \__ _| |_ __ _| |__   __ _ ___  ___ 
#   //_\\ / __| __| \ \ / / | __| | | |   / /\ / _` | __/ _` | '_ \ / _` / __|/ _ \
#  /  _  \ (__| |_| |\ V /| | |_| |_| |  / /_// (_| | || (_| | |_) | (_| \__ \  __/
#  \_/ \_/\___|\__|_| \_/ |_|\__|\__, | /___,' \__,_|\__\__,_|_.__/ \__,_|___/\___|
#                                |___/                                             

import os
import asyncio
import asyncpg

from .db_default import NPDefaultDB

class NPActivityInfoDB(NPDefaultDB):
    def __init__(self, db):
        super().__init__(db, table_name='activity_info')

class NPClientActivityDB(NPDefaultDB):
    def __init__(self, db):
        super().__init__(db, table_name='client_activities')