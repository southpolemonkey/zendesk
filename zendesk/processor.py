import click
from pprint import pprint

from .db import Database

class Processor():
    """
    Client query processor
    """

    def __init__(self):
        self._name = 'processor'
        self.item = None

    def search(self, db, item, field, value):
        results = []
        if item == '1':
            data = db.collections.get('users')
        elif item == '2':
            data = db.collections.get('tickets')
        elif item == '3':
            data = db.collections.get('organizations')
        else:
            data = []

        for row in data:
            target = row.get(field)
            if target == value:
                results.append(row)
        return results


    def ask(self):
        item = click.prompt("Select 1: Users or 2: Tickets or 3: Organizations", type=str)
        field = click.prompt("Enter search field", type=str)
        value = click.prompt("Enter search value", type=int)

        db = Database()

        click.echo(f"Searching {field} match {value} from {item}")

        results = self.search(db, item, field, value)
        self.present(results)


    def present(self, results):
        for result in results:
            pprint(result)




