import json
import os.path
from typing import Dict, List, Iterable, Any, Optional, Union
from collections import defaultdict
from dataclasses import dataclass, field

from .utilties import get_logger
from .model import Organizations, Tickets, Users

logger = get_logger(__name__)

resources = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources')

class TableNotExistsException(Exception):
    pass

class ColumnNotExistsException(Exception):
    pass


@dataclass
class Index():
    '''
    Index class
    Example
    name: _id
    references: {71: [1], 52: [3]}
    '''
    name: str
    references: Dict[str, List] = field(default_factory=lambda: defaultdict(list))

    def search(self, key: Union[int, str]) -> Optional[List]:
        return self.references.get(key)



@dataclass
class Table():
    name: str
    # TODO: design primary key and foreign key structure
    primary_key: str = ""
    foreign_key: str = ""
    records: List[Dict[Any, Any]] = field(default_factory=list)
    indexes: Dict[str, Index] = field(default_factory=lambda: defaultdict(Index))

    def build_index(self):
        '''
        Construct index data structure
        '''
        idx_col = self.primary_key
        idx = Index(idx_col)
        for i, record in enumerate(self.records):
            key = record.get(idx_col)
            idx.references[key].append(i)

        self.indexes[idx_col] = idx


    def _search_by_index(self, field, value) -> Optional[List[int]]:
        '''
        Search by field value and return the index of occurrence
        '''

        if index_record := self.indexes.get(field):
            reference = index_record.search(value)
            return reference

    def _sequential_search(self, field, value) -> List:
        res = []
        for record in self.records:
            if find := record.get(field):
                if find == value:
                    res.append(record)
        return res


    def search(self, field, value) -> List:
        # TODO: sentinel check field exists
        indexes = self._search_by_index(field, value)

        if indexes:
            res = [self.records[i] for i in indexes]
            return res
        else:
            res = self._sequential_search(field, value)
            return res



class Database():
    def __init__(self):
        self.name: str = 'zendesk'
        self.collections: Dict[str, Table] = {}

    def load(self, tables: List[str] = ['tickets', 'organizations', 'users']) -> None:
        '''
        Load files matching names in the give @tables parameters
        '''

        index_keys = {
            'users': '_id',
            'organizations': '_id',
            'tickets': 'submitter_id'

        }

        for table_name in tables:
            filename = os.path.join(resources, table_name + '.json')
            logger.info(f'Loading {filename}')

            idx = index_keys.get(table_name)

            table = Table(name=table_name, primary_key=idx)

            try:
                with open(filename, 'r') as f:
                    source = json.load(f)
                    table.records = source
                    self.collections[table_name] = table
                    table.build_index()
            except FileNotFoundError:
                logger.error(f'{filename} not exists')

    def search(self, entity, field, value):
        table = self.collections.get(entity)
        if table:
            res = table.search(field, value)
            return res
        else:
            raise TableNotExistsException






