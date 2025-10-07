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
    # setup argument parsing (argv for testing)
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    connection = db_connect()
    # HACK: we're creating the connection twice: once here, and again in
    # each of the cli handler functions... this is going to cause a problem...

    try:
        # setup / connect to local database
        create_table(connection)

        # execute commands from cli arguments (see cli.py for handling)
        args.func(args)

    except Exception as err:
        print("Error in __main__: ", err)
    finally:
        connection.close()  # finally close db connection


if __name__ == "__main__":
    main()
