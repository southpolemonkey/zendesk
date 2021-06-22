import pytest
from zendesk.processor import Processor
from zendesk.db import Database, Table, Index, TableNotExistsException, ForeignKeys

from typing import Dict

@pytest.fixture()
def db():
    db = Database()
    db.load()
    return db

@pytest.fixture()
def users(db) -> Table:
    return db.collections.get('users')

@pytest.fixture()
def organizations(db) -> Table:
    return db.collections.get('organizations')

@pytest.fixture()
def tickets(db) -> Table:
    return db.collections.get('tickets')


@pytest.fixture()
def processor():
    processor = Processor()
    return processor

class TestProcessor:

    def test_initialise_processor(self, processor):

        assert isinstance(processor, Processor)

    def test_parse_query(self, processor):
        query = "search users organization_id value could be long string and contains @?"
        entity, field, value = processor.parse_query(query)
        assert entity == "users"
        assert field == "organization_id"
        assert value == "value could be long string and contains @?"


class TestDatabase:

    def test_load(self, db):
        for table_name, collections in db.collections.items():
            assert isinstance(table_name, str)
            assert isinstance(collections, Table)

    def test__exception(self, db):
        with pytest.raises(TableNotExistsException):
            db.search('table_not_exists', 'field', 'value')


class TestTable:


    def test_build_index(self, users):
        users_indexes = users.indexes
        for key, index in users_indexes.items():
            assert isinstance(key, str)
            assert isinstance(index, Index)

    def test_search(self, users):
        res = users.search('organization_id', "104", alias={'_id': 'user_id', 'name:': 'user_name'})
        assert len(res) == 4

    def test_join(self, users, organizations, tickets):
        res = users.search('_id', '71')
        fks = [
            ForeignKeys('organization_id', '_id', organizations, alias={'name':"organization_name"}),
            ForeignKeys('_id', 'submitter_id', tickets, alias={'subject':'ticket_subject'}),
        ]
        enriched = users.join(res, fks)
        assert len(enriched[0].get('organizations')) == 1
        assert len(enriched[0].get('tickets')) == 3



class TestIndex:

    def test_initialisation_index(self):
        index = Index('_id')
        assert index.references == {}

class TestForeignKey:

    def test_initialize_foreign_key(self):
        fk = ForeignKeys('submitter_id', '_id', None)
        assert isinstance(fk, ForeignKeys)



