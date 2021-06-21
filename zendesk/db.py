import json
import os.path
from typing import Dict, List, Any, Optional
from collections import defaultdict
from dataclasses import dataclass, field

from .utilties import get_logger
from .model import Organizations, Tickets, Users

logger = get_logger(__name__)

resources = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources")


class TableNotExistsException(Exception):
    pass


class ColumnNotExistsException(Exception):
    pass

@dataclass
class ForeignKeys:
    foreign_table:str
    foreign_key:str
    local_key:str
    local_table:str


fks = {
    'users': [
        ForeignKeys(local_key="organization_id", local_table="users", foreign_key="_id", foreign_table="organization")]
    ,
    'tickets': [
        ForeignKeys(local_key="submitter_id", local_table="tickets", foreign_key="_id", foreign_table="users"),
        ForeignKeys(local_key="organization_id", local_table="tickets", foreign_key="_id",foreign_table="organization")
    ]
}


@dataclass
class Index:
    """
    Index class
    Example
    name: _id
    references: {71: [1], 52: [3]}
    """

    name: str
    references: Dict[str, List[Any]] = field(default_factory=lambda: defaultdict(list))

    def search(self, key: str) -> Optional[List[Any]]:
        return self.references.get(key)


@dataclass
class Table:
    name: str
    # TODO: hardcode foreign key in a dictionary for each table
    primary_key: str = ""
    foreign_key: List[ForeignKeys] = field(default_factory=list)
    records: List[Dict[Any, Any]] = field(default_factory=list)
    indexes: Dict[str, Index] = field(default_factory=lambda: defaultdict(Index))

    def build_index(self) -> None:
        """
        Construct index data structure
        """
        logger.info(f"Building index...{self.name}")
        idx_col = self.primary_key
        idx = Index(idx_col)
        for i, record in enumerate(self.records):
            key = str(record.get(idx_col))
            idx.references[key].append(i)

        self.indexes[idx_col] = idx

    def add_foreign_keys(self)-> None:
        self.foreign_key = fks.get(self.name, [])


    def _search_by_index(self, field: str, value: str) -> Optional[List[int]]:
        """
        Search by field value and return the index of occurrence
        """

        if index_record := self.indexes.get(field):
            reference = index_record.search(str(value))
            return reference

    def _sequential_search(self, field: str, value: str) -> List[Any]:
        res = []
        for record in self.records:
            if find := record.get(field):
                if str(find) == value:
                    res.append(record)
        return res

    def _fetch_foreign_fields(self):
        raise NotImplementedError
    
    # TODO: search foreign keys
    def search(self, field: str, value: str) -> List[Any]:

        logger.debug(f"{self.name}: searching {field}={value}")
        indexes = self._search_by_index(field, value)

        if indexes:
            res = [self.records[i] for i in indexes]
            return res
        else:
            res = self._sequential_search(field, value)
            return res


class Database:
    def __init__(self):
        self.name: str = "zendesk"
        self.collections: Dict[str, Table] = {}

    def load(self, tables: List[str] = ["tickets", "organizations", "users"]) -> None:
        """
        Load files matching names in the give @tables parameters
        """

        pkeys = {"users": "_id", "organizations": "_id", "tickets": "submitter_id"}

        for table_name in tables:
            filename = os.path.join(resources, table_name + ".json")
            logger.info(f"Loading {filename}")


            table = Table(name=table_name, primary_key=pkeys.get(table_name,""), foreign_key=fks.get(table_name, []))

            try:
                # TODO: lazy load bigfile
                with open(filename, "r") as f:
                    source = json.load(f)
                    table.records = source
                    self.collections[table_name] = table
                    table.build_index()
                    table.add_foreign_keys()
            except FileNotFoundError:
                logger.error(f"{filename} not exists")

    def search(self, entity: str, field: str, value: str) -> List:
        table = self.collections.get(entity)
        logger.debug(f"searching {table}: {field}={value}")
        if table:
            res = table.search(field, value)
            return res
        else:
            raise TableNotExistsException
