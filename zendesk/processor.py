import os
from typing import Dict, List

import click

from .utilties import get_logger, read_yaml
from .db import Database
from .model import Organizations, Tickets, Users

logger = get_logger(__name__)

global database

DATAMODELS = {"organization": Organizations, "ticket": Tickets, "users": Users}

YAML = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.yaml")


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

    def load_db(self, yaml_fpath: str = YAML):
        schema = read_yaml(yaml_fpath)

        global database
        database = Database()
        database.load(schema)

    def drop_db(self):
        global database
        del database
        click.echo("Dropped all tables!")

    def handle(self, query: str):
        global database
        parsed, is_match = self.parse_query(query)
        if is_match:
            entity, field, value = parsed
            try:
                if res := database.search(entity, field, value):
                    self.present(res)
            # except TableNotExistsException:
            #     click.echo(f"{entity} not found in database")
            except NameError:
                if click.confirm(
                    "Database is not connected yet, could you like to connect?"
                ):
                    self.load_db()

    def parse_query(self, query: str):

        import re

        if match := re.match(
            r"(search)\s(\w+)\s(\w+)\s?([\w+\s.+=\-!?@()\[\]<>\/\\|\$\&\*-:\*]{0,})$",
            query,
        ):
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

    def show_tables(self) -> None:
        """
        List all fields in each table
        """
        print("Searchable fields")

        for name, model in DATAMODELS.items():
            columns = model.__annotations__.keys()
            print(f"{name}")
            print("=" * 20)
            for col in columns:
                print(col)
            print()

    def show_db(self) -> None:
        """
        List all tables in database
        """
        try:
            global database
            for table in database.collections.keys():
                print(table)
        except NameError:
            if click.confirm(
                "Database is not connected yet, could you like to connect?"
            ):
                self.load_db()
