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
        help                                show help information
        
        load                                load data 
        search                              interactive query mode
        search <entity> <field> <value>         
        show db                             list all tables
        show table                          list all fields
        
        quit
    """
    )


@click.command()
@click.option("--command", default="help", help="Choose command")
def main(command):

    header = pyfiglet.figlet_format("Zendesk bot", font="slant")
    print(header)

    process = Processor()

    while True:
        choice = str.lower(click.prompt("> ", type=str)).strip()

        if choice in ("exit", "quit"):
            print("Bye")
            break
        elif choice == "help":
            help()
        elif choice == "show table":
            process.show_tables()
        elif choice == "show db":
            process.show_db()
        elif choice == "load":
            process.load_db()
        elif choice == "search":
            process.ask()
        elif choice.startswith("search"):
            process.handle(choice)
        elif choice == "clear":
            click.clear()
        else:
            print("Invalid command")
            help()


if __name__ == "__main__":
    main()
