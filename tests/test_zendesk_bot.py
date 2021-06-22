import pytest
from zendesk.processor import Processor
from zendesk.db import Database, Table, Index, TableNotExistsException, ForeignKeys
from zendesk.utilties import read_yaml

from typing import Dict


@pytest.fixture()
def db():
    db = Database()
    schemadef = read_yaml('../config.yaml')
    db.load(schemadef)
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

    def test_handle(self, processor):
        query = "search tickets created_at 2016-04-14T08:32:31 -10:00"
        _, is_match = processor.parse_query(query)
        assert is_match == True

    def test_parse_query(self, processor):
        query = "search users organization_id value could be long string and contains @?"
        entity, field, value = processor.parse_query(query)[0]
        assert entity == "users"
        assert field == "organization_id"
        assert value == "value could be long string and contains @?"

    def test_present(self, processor):
        res = [{
            "_id": 1,
            "url": "http://initech.zendesk.com/api/v2/users/1.json",
            "external_id": "74341f74-9c79-49d5-9611-87ef9b6eb75f",
            "name": "Francisca Rasmussen",
            "tickets": [
                {"subject": "A Catastrophe in Micronesia", "priority": "low"},
                {"subject": "Other ticket", "priority": "high"},
            ],
            "organizations": [
                {"organization_name": "zendesk"}
            ]
        }]

        processor.present(res)


class TestDatabase:

    def test_load(self, db):
        for table_name, collections in db.collections.items():
            assert isinstance(table_name, str)
            assert isinstance(collections, Table)

        assert len(db.collections) == 3

    def test_search(self, db):
        res = db.search('users', "name", "Francisca Rasmussen")
        assert len(res[0].get('organizations')) >= 1
        assert len(res[0].get('tickets')) >= 1


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
        res = users.search('organization_id', "104", alias=[{'alias': 'organization_name', 'field': 'name'}])
        assert len(res) == 4

    def test_join(self, users, organizations, tickets):
        res = users.search('_id', '71')
        fks = [
            ForeignKeys('organization_id', '_id', organizations, alias=[{'name': "organization_name"}]),
            ForeignKeys('_id', 'submitter_id', tickets, alias=[{'subject': 'ticket_subject'}]),
        ]

        enriched = users.join(res, fks)
        assert len(enriched[0].get('organizations')) == 1
        assert len(enriched[0].get('tickets')) == 3

    def test_join_2(self, users, organizations, tickets):
        res = users.search('_id', '71')
        enriched = users.join(res, [])
        assert enriched[0].get('organizations') is None
        assert enriched[0].get('tickets') is None

class TestIndex:

    def test_initialisation_index(self):
        index = Index('_id')
        assert index.references == {}

class TestForeignKey:

    def test_initialize_foreign_key(self):
        fk = ForeignKeys('submitter_id', '_id', None)
        assert isinstance(fk, ForeignKeys)
