from typing import List
from dataclasses import dataclass


@dataclass
class Organizations:
    _id: int
    url: str
    external_id: str
    name: str
    domain_names: List[str]
    created_at: str
    details: str
    shared_tickes: str
    tags: List[str]


@dataclass
class Tickets:
    _id: str
    url: str
    external_id: str
    created_at: str
    type: str
    subject: str
    description: str
    priority: str
    status: str
    submitter_id: str
    assignee_id: int
    organization_id: str
    tags: List[str]
    has_incidents: str
    due_at: str
    via: str


@dataclass
class Users:
    _id: int
    url: str
    external_id: str
    alias: str
    created_at: str
    active: bool
    verified: bool
    shared: bool
    locale: str
    timezone: str
    last_login_at: str
    email: str
    phone: str
    signature: str
    organization_id: str
    tags: List[str]
    suspended: bool
    role: bool
