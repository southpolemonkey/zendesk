import pytest
from zendesk.processor import Processor
from zendesk.db import Database, Table, Index, TableNotExistsException

from typing import Dict

@pytest.fixture()
def db():
    db = Database()
    db.load()
    return db


class TestProcessor:

    def test_initialise_processor(self):
        processor = Processor()
        assert isinstance(processor, Processor)


class TestDatabase:

    def test_load(self, db):
        for table_name, collections in db.collections.items():
            assert isinstance(table_name, str)
            assert isinstance(collections, Table)

    def test__exception(self, db):
        with pytest.raises(TableNotExistsException):
            db.search('table_not_exists', 'field', 'value')


class TestTable:

    def test_build_table(self, db):
        users = db.collections.get('users')

    def test_build_index(self, db):
        users_indexes = db.collections.get('users').indexes
        for key, index in users_indexes.items():
            assert isinstance(key, str)
            assert isinstance(index, Index)

    def test__search_field_index(self, db):
        users_table = db.collections.get('users')
        res = users_table._search_by_index('_id', 1)
        assert isinstance(res, list)

    def test__search_field_no_index(self, db):
        users_table = db.collections.get('users')
        res = users_table._sequential_search('organization_id', "104")
        assert len(res) >= 1


class TestIndex:

    def test_initialisation_index(self):
        index = Index('_id')
        assert index.references == {}



