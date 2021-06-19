from dataclasses import dataclass
from typing import Dict, Optional, List

import click

from .db import Database
from .utilties import get_logger


logger = get_logger(__name__)

global database


@dataclass
class UserQueryResponse:
    pass


@dataclass
class OrganizationQueryResponse:
    pass


@dataclass
class TicketQueryResponse:
    pass


class Processor:
    """
    Query order processor
    """

    def __init__(self):
        self._name = "processor"

    def ask(self) -> None:
        """
        Interactive query mode
        """

        global database

        entity = click.prompt("Enter search table", type=str)
        field = click.prompt("Enter search field", type=str)
        value = click.prompt("Enter search value", type=str)

        click.echo(f"Searching {field} match {value} from {entity}")

        try:
            res = database.search(entity, field, value)
            logger.debug(res)
            self.present(res)
        except NameError:
            if click.confirm(
                "Database is not connected yet, could you like to connect?"
            ):
                self.load_db()

    def present(self, results: List[Dict]) -> None:
        """
        beautify json objects
        """
        print("Results:\n")
        for result in results:
            for k, v in result.items():
                if isinstance(v, list):
                    print("{:<20}|{:>50}".format(k, ", ".join(v)))
                else:
                    print("{:<20}|{:>50}".format(k, v))
            print()

    def load_db(self):
        global database
        database = Database()
        database.load()

    def parse_query(self, query: str) -> Optional[Dict]:
        global database
        try:
            import re

            if match := re.match(r"(^search)\s(\w+)\s(\w+)\s(\w+\s?\w?)$", query):
                if len(match.groups()) == 4:
                    entity = match.groups()[1]
                    field = match.groups()[2]
                    value = match.groups()[3]
                    logger.debug(f"Search {entity} {field} {value}")
                    res = database.search(entity, field, value)
                    if res:
                        self.present(res)
            else:
                click.echo(
                    """
                    Unrecognized query pattern. 
                    Use:  
                        search (interactive model)
                        search <entity> <field> <value>
                """
                )
        except NameError:
            if click.confirm(
                "Database is not connected yet, could you like to connect?"
            ):
                self.load_db()

    def list_searchable_fields(self) -> None:
        # TODO: implement
        print("Method not implemented yet")
