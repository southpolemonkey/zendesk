from .db import Database
from .processor import Processor

import click

def list_searchable_fields():
    print("Getting searchable fields")

@click.command()
def main():

    choice = click.prompt("""
    Select search options:
    1: Search zendesk
    2: View a list of searchable fields
    """, type=str)

    if choice == "1":
        processor = Processor()
        processor.ask()

    elif choice == "2":
        list_searchable_fields()
    else:
        click.exceptions("Invalid options")



if __name__ == "__main__":
    main()
