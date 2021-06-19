import pyfiglet
import click

from .processor import Processor


@click.group()
def cli():
    pass


def help():
    print(
        """
    Commands:
        help
        search
        search <entity> <field> <value>
        load
        quit
        fields
    """
    )


@click.command()
@click.option("--command", default="help", help="Choose command")
def main(command):

    header = pyfiglet.figlet_format("Zendesk bot", font="slant")
    print(header)

    process = Processor()

    while True:
        choice = str.lower(click.prompt("Command: ", type=str)).strip()

        if choice in ("exit", "quit"):
            print("Bye")
            break
        elif choice == "help":
            help()
        elif choice == "fields":
            process.list_searchable_fields()
        elif choice == "load":
            process.load_db()
        elif choice == "search":
            process.ask()
        elif choice.startswith("search"):
            res = process.parse_query(choice)
            if res:
                print("Invalid query pattern")
        elif choice == "clear":
            click.clear()
        else:
            print("Invalid command")


if __name__ == "__main__":
    main()
