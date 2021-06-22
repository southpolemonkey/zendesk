from __future__ import annotations
import json
import os.path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
from dataclasses import dataclass, field

from .utilties import get_logger

logger = get_logger(__name__)

resources = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources")


class TableNotExistsException(Exception):
    pass


class ColumnNotExistsException(Exception):
    pass


@dataclass
class ForeignKeys:
    field: str
    foreign_key: str
    foreign_table: Table
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
    foreign_key: List[Dict[str, Tuple[str, str]]] = field(
        default_factory=defaultdict(list)
    )
    index_key: List[str] = field(default_factory=list)
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

    def _sequential_search(
        self, field: str, value: str, alias: List[Dict[str, str]] = "all"
    ) -> List[Any]:
        logger.info(f"Seq scan {self.name} {field} {value} {alias}")
        res = []
        for record in self.records:
            if find := record.get(field):
                if str(find).lower() == str(value).lower():
                    if alias == "all":
                        res.append(record)
                    elif isinstance(alias, list):
                        filtered = {}
                        for ele in alias:
                            k = ele.get('field')
                            v = ele.get('alias')
                            if k in record:
                                filtered[v] = record.get(k)
                            # filtered = {
                            #     alias.get(k): v for k, v in record.items() if k in alias
                            # }
                        res.append(filtered)
                    else:
                        continue
        return res

    def join(self, records: List[Dict], fks: List[ForeignKeys]) -> List[Any]:
        """
        Implementation of enrich table with external fields
        """
        for record in records:
            for fk in fks:
                field = fk.field
                foreign_key = fk.foreign_key
                foreign_table = fk.foreign_table
                alias = fk.alias

                if value := record.get(field):
                    res = foreign_table.search(foreign_key, value, alias=alias)
                    record[foreign_table.name] = res

        return records

    def search(
        self, field: str, value: str, alias: List[Dict[str, str]] = "all"
    ) -> List[Any]:
        """
        Search interface by default returns all fields from the collections.
        :param field: field name
        :param value: value to search for
        :param alias:
            @key    selected fields
            @value  alias in response

        example:
        alias =  [{'alias': 'organization_name', 'field': 'name'}]
        """

        logger.info(f"{self.name}: searching {field}={value}")
        indexes = self._index_search(field, value)

        if indexes:
            res = []
            for i in indexes:
                if alias == "all":
                    record = self.records[i]
                    res.append(record)
                elif isinstance(alias, list):
                    record = self.records[i]
                    filtered = {}
                    for ele in alias:
                        k = ele.get('field')
                        v = ele.get('alias')
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

    def load(self, schemadef: Dict[str, Any]) -> None:
        """
        Build database from the given schema object
        """
        tables = schemadef.get('tables')
        for table_name, schema in tables.items():

            filename = os.path.join(resources, table_name + ".json")
            logger.info(f"Loading {table_name} from {filename}")

            index = schema.get('index')
            primary_key = schema.get('primary_key')
            external_fields =  schema.get('external_fields')

            try:
                table = Table(
                    name=table_name,
                    primary_key=primary_key,
                    foreign_key=external_fields,
                    index_key=index,
                )

                # TODO: lazy load bigfile
                with open(filename, "r") as f:
                    source = json.load(f)
                    table.records = source
                    self.collections[table_name] = table
                    table.build_index()
                    print(f"{table_name} loads successfully!")
            except FileNotFoundError:
                logger.error(f"{filename} not exists")
                print(f"{table_name} failed. {filename} not exists")

    def fetch_collection(self, entity: str) -> Table:
        table = self.collections.get(entity)
        if table:
            return table
        else:
            raise TableNotExistsException

    def search(self, entity: str, field: str, value: str) -> List:
        logger.debug(f"searching {entity}: {field}={value}")

        table = self.fetch_collection(entity)

        res = table.search(field, value)
        if foreign_keys := table.foreign_key:

            foreign_key_list = []
            for foreign_key in foreign_keys:
                query = ForeignKeys(
                        foreign_key.get('local_table_key'),
                        foreign_key.get('external_table_key'),
                        self.fetch_collection(foreign_key.get('external_table_name')),
                        foreign_key.get('required_fields')
                    )

                foreign_key_list.append(query)

            enriched = table.join(res, foreign_key_list)
            return enriched
        else:
            return res

        # if table.name == "users":

            # fks = [
            #     ForeignKeys(
            #         "organization_id",
            #         "_id",
            #         self.fetch_collection("organizations"),
            #         alias={"name": "organization_name"},
            #     ),
            #     ForeignKeys(
            #         "_id",
            #         "submitter_id",
            #         self.fetch_collection("tickets"),
            #         alias={"subject": "ticket_subject"},
            #     ),
            # ]
            # enriched = table.join(res, ffks)
            # return enriched
        # if table.name == "tickets":
        #     res = table.search(field, value)
        #     fks = [
        #         ForeignKeys(
        #             "submitter_id",
        #             "_id",
        #             self.fetch_collection("users"),
        #             alias={"name": "user_name", "email": "user_email"},
        #         ),
        #         ForeignKeys(
        #             "organization_id",
        #             "_id",
        #             self.fetch_collection("organizations"),
        #             alias={"name": "organization_name"},
        #         ),
        #     ]
        #     enriched = table.join(res, fks)
        #     return enriched
        # else:
        #     res = table.search(field, value)
        #     return res
