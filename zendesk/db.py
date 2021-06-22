from __future__ import annotations
import json
import os.path
from typing import Dict, List, Any, Optional, Tuple, Iterable
from collections import defaultdict
from dataclasses import dataclass, field

from .utilties import get_logger
from .config import fkeys, pkeys, idx_keys
from .model import UsersQueryResponse, TicketsQueryResponse, OrganizationQueryResponse

logger = get_logger(__name__)

resources = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources")

class TableNotExistsException(Exception):
    pass


class ColumnNotExistsException(Exception):
    pass

@dataclass
class ForeignKeys:
    field:str
    foreign_key:str
    foreign_table:Table
    alias: Dict[str, str] = field(default_factory=lambda: defaultdict)

@dataclass
class Index:
    """
    Index class

    name: name of the field index builds upon
    references:
        @key: value in _id
        @value: index to the record contains the matching key

    Example
    data: [{"_id": "71"}, {"_id": "52"}, {"_id": "52"}]
    index: {"71": [0], "52": [1,2]}
    """

    name: str
    references: Dict[str, List[Any]] = field(default_factory=lambda: defaultdict(list))

    def search(self, key: str) -> Optional[List[Any]]:
        return self.references.get(key)


@dataclass
class Table:
    name: str
    primary_key: str = ""
    foreign_key: List[Dict[str, Tuple]] = field(default_factory=defaultdict(list))
    index_key: List = field(default_factory=list)
    records: List[Dict[Any, Any]] = field(default_factory=list)
    indexes: Dict[str, Index] = field(default_factory=lambda: defaultdict(Index))


    def _build_index(self, k: str) -> None:
        idx = Index(k)
        for i, record in enumerate(self.records):
            key = str(record.get(k))
            idx.references[key].append(i)
        self.indexes[k] = idx


    def build_index(self) -> None:
        """
        Construct index data structure
        """
        logger.info(f"Building primary index...{self.name}")
        pk = self.primary_key
        if pk != "":
            self._build_index(pk)

        if len(self.index_key) > 0:
            for k in self.index_key:
                if k != self.primary_key:
                    self._build_index(k)


    def _index_search(self, field: str, value: str) -> Optional[List[int]]:
        """
        Search by field value and return the index of occurrence
        """
        logger.info(f"indexing search...{self.name}: {field} {value}")
        if index_record := self.indexes.get(field):
            reference = index_record.search(str(value))
            return reference

    def _sequential_search(self, field: str, value: str, alias: Dict[str, str] = "all") -> List[Any]:
        res = []
        for record in self.records:
            if find := record.get(field):
                if str(find) == value:
                    if alias == "all":
                        res.append(record)
                    elif isinstance(alias, dict):
                        filtered =  {alias.get(k): v for k, v in record.items() if k in alias}
                        res.append(filtered)
                    else:
                        continue
        return res

    def join(self, records: List[Dict], fks: List[ForeignKeys]) -> List[Any]:
        '''
        Implementation of enrich table with external fields
        '''
        for record in records:
            for fk in fks:
                field = fk.field
                foreign_key = fk.foreign_key
                foreign_table = fk.foreign_table
                alias = fk.alias

                value = record.get(field)
                res = foreign_table.search(foreign_key, value, alias=alias)
                record[foreign_table.name] = res

        return records

    def search(self, field: str, value: str, alias: Dict[str, str] = "all") -> List[Any]:
        '''
        Search interface by default returns all fields from the collections.
        :param field: field name
        :param value: value to search for
        :param alias:
            @key    selected fields
            @value  alias in response
        :return:
        '''

        logger.debug(f"{self.name}: searching {field}={value}")
        indexes = self._index_search(field, value)

        if indexes:
            res = []
            for i in indexes:
                if alias== "all":
                    record = self.records[i]
                    res.append(record)
                elif isinstance(alias, dict):
                    record = self.records[i]
                    filtered = {}
                    for k, v in alias.items():
                        if k in record:
                            filtered[v] = record.get(k)
                    res.append(filtered)
                else:
                    continue

            return res
        else:
            res = self._sequential_search(field, value, alias)
            return res


class Database:
    def __init__(self):
        self.name: str = "zendesk"
        self.collections: Dict[str, Table] = {}

    def load(self, tables: List[str] = ["tickets", "organizations", "users"]) -> None:
        """
        Load files matching names in the give @tables parameters
        """

        for table_name in tables:
            filename = os.path.join(resources, table_name + ".json")
            logger.info(f"Loading {filename}")

            table = Table(
                name=table_name,
                primary_key=pkeys.get(table_name,""),
                foreign_key=fkeys.get(table_name, []),
                index_key=idx_keys.get(table_name, [])
            )

            try:
                # TODO: lazy load bigfile
                with open(filename, "r") as f:
                    source = json.load(f)
                    table.records = source
                    self.collections[table_name] = table
                    table.build_index()
            except FileNotFoundError:
                logger.error(f"{filename} not exists")

    def fetch_collection(self, entity: str) -> Table:
        table = self.collections.get(entity)
        if table:
            return table
        else:
            raise TableNotExistsException


    def search(self, entity: str, field: str, value: str) -> List:
        logger.debug(f"searching {entity}: {field}={value}")

        table = self.fetch_collection(entity)

        if table.name == 'users':
            res = table.search(field, value)
            fks = [
                ForeignKeys('organization_id', '_id', self.fetch_collection('organizations'), alias={'name':"organization_name"}),
                ForeignKeys('_id', 'submitter_id', self.fetch_collection('tickets'), alias={'subject':'ticket_subject'})
            ]
            enriched = table.join(res, fks)
            return enriched
        if table.name == 'tickets':
            res = table.search(field, value)
            fks = [
                ForeignKeys('submitter_id', '_id', self.fetch_collection('users'), alias={'name':"user_name", 'email': 'user_email'}),
                ForeignKeys('organization_id', '_id', self.fetch_collection('organizations'), alias={'name':"organization_name"})
            ]
            enriched = table.join(res, fks)
            return enriched
        else:
            res = table.search(field, value)
            return res

