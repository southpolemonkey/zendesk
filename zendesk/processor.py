from typing import Dict, List
from .model import Organizations, Tickets, Users

import click

from .db import Database
from .utilties import get_logger


logger = get_logger(__name__)

global database

DATAMODELS = {'organization': Organizations, 'ticket': Tickets, 'users': Users}


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

        def _present(result: Dict):
            for k, v in result.items():
                try:
                    if isinstance(v, list):
                        try:
                            if isinstance(v[0], str):
                                print("{:<20}|{:>50}".format(k, ", ".join(v)))
                            elif isinstance(v[0], dict):
                                for ele in v:
                                    _present(ele)
                        except IndexError:
                            continue
                    else:
                        print("{:<20}|{:>50}".format(k, v))
                except TypeError:
                    pass

        for result in results:
            _present(result)
            print()

    def load_db(self):
        global database
        database = Database()
        database.load()

    def handle(self, query: str):
        parsed, is_match = self.parse_query(query)
        if is_match:
            entity, field, value = parsed
            if res := database.search(entity, field, value):
                self.present(res)

    def parse_query(self, query: str):
        global database
        try:
            import re
            if match := re.match(r"(search)\s(\w+)\s(\w+)\s?([\w+\s.+=\-!?@()\[\]<>\/\\|\$\&\*-:\*]{0,})$", query):
                if len(match.groups()) == 4:
                    entity = match.groups()[1]
                    field = match.groups()[2]
                    value = match.groups()[3]
                    logger.info(f"Search {entity} {field} {value}")
                    return (entity, field, value), True
            else:
                click.echo(
        """
        Unrecognized query pattern. 
        Use:  
            search (interactive model)
            search <entity> <field> <value>
    """
)
                return "", False
        except NameError:
            if click.confirm(
                "Database is not connected yet, could you like to connect?"
            ):
                self.load_db()


    def list_searchable_fields(self) -> None:

        print("Searchable fields")

        for name, model in DATAMODELS.items():
            columns = model.__annotations__.keys()
            print(f"{name}")
            print(f"="*20)
            for col in columns:
                print(col)
            print()

