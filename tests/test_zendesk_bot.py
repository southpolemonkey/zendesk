import pytest
from zendesk.processor import Processor
from zendesk.db import Database

@pytest.fixture()
def db():
    db = Database()
    return db

def test_search_field_by_value(db):

    process = Processor()

    item = '1'
    field = '_id'
    value = '71'

    result = process.search(db, item, field, value)
    assert len(result) == 1