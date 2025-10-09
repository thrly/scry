# Main entry point for SCRY: a command-line scryfall query tool
# by thrly


from . import (
    create_table,
    db_connect,
)
from .cli import (
    build_arg_parser,
)


def main(argv=None):
    connection = db_connect()

    # setup argument parsing (argv for testing)
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    try:
        # setup / connect to local database
        create_table(connection)

        # execute commands from cli arguments (see cli.py for handling)
        args.func(args, connection)

    except Exception as err:
        print("Error in main(): ", err)
    finally:
        connection.close()  # finally close db connection


if __name__ == "__main__":
    main()
