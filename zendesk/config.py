import logging

LOGGER_LEVEL = logging.INFO

pkeys = {
    "users": "_id",
    "organizations": "_id",
    "tickets": "_id"
}

fkeys = {
    'users': [
        {"_id": ("organization", "organization_id")},
    ]
    ,
    'tickets': [
        {"submitter_id": ("users", "_id")},
        {"organization_id": ("organization", "organization_id")},
    ]
}


idx_keys = {
    "users": ["_id"],
    "organizations": ["_id"],
    "tickets": ["submitter_id", "organization_id"]
}

