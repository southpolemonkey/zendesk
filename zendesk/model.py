from typing import Optional, List


class Organizations():
    def __init__(self):
        self._id: int = None,
        self.url: str = None,
        self.external_id: str = None,
        self.name: str = None,
        self.domain_names: List[str] = None,
        self.created_at: str = None,
        self.details: str = None,
        self.shared_tickes: str = None,
        self.tags: List[str]


class Tickets():
    def __init__(self):
        pass


class Users():
    def __init__(self):
        pass