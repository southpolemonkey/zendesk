import json
import os.path
from typing import Dict

from .model import Organizations, Tickets, Users

class TableNotExistsException(Exception):
    pass

class Database():
    def __init__(self):
        self.collections = {}

    def load_data(self) -> Dict:

        tables = ['tickets', 'users', 'organizations']
        dir = os.path.dirname(os.path.realpath(__file__))
        for table in tables:
            filename = os.path.join(dir, type + '.json')
            with open(filename, 'r') as f:
                data = json.load(f)
                self.collections[table] = data





