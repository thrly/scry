import argparse
from datetime import datetime
from . import (
    get_random_card,
    insert_cards,
    get_card_list,
    db_stats,
    get_total_cards,
    clear_database,
    set_codes,
    db_connect,
)


def build_arg_parser() -> argparse.ArgumentParser:
    # setup parser and sub command parsers
    parser = argparse.ArgumentParser(
        description="🃏 Query cards from Scryfall and draw stats from a set.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            """
    Examples:
        scry random -n 3
        scry search t:creature c:g
        scry set BLB
    """
        ),
    )
    subparsers = parser.add_subparsers(
        # dest="subcommand",
        title="subcommands",
        description="Basic scrying functions. Some require additional parameters.",
        required=True,
    )

    # Define each subcommand:
    # RANDOM ------------------------
    random_parser = subparsers.add_parser(
        "random",
        help="Draw random cards from Scryfall",
    )
    random_parser.add_argument(
        "-n",
        "--number",
        type=int,
        default=1,
        help="Number of random cards to draw",
    )
    random_parser.set_defaults(func=handle_random)

    # SEARCH ------------------------
    # TODO: bypass this completely and just run with `scry <search_query>`
    list_parser = subparsers.add_parser(
        "search", help="Returns a list of cards matching search parameters"
    )
    list_parser.add_argument(
        "search_query",
        nargs="+",
        help="Argument as Scryfall-syntax search query (e.g. 't:creature+c:green')",
        # TODO: is it possible to set a default value if no query arg is given? 't:land' etc.
    )
    list_parser.set_defaults(func=handle_search)

    # SET ------------------------
    set_parser = subparsers.add_parser("set")
    set_parser.add_argument(
        "set_query",
        help="Specify setcode (run `scry setcodes` for reference) or 'latest'",
    )
    set_parser.set_defaults(func=handle_set)

    # SETCODES ------------------------
    setcodes_parser = subparsers.add_parser(
        "setcodes",
        help="Return list of sets with code, card total, and year of release",
    )
    setcodes_parser.set_defaults(func=handle_setcodes)

    # STATS -----------------------
    stats_parser = subparsers.add_parser(
        "stats", help="Return stats for current database"
    )
    # TODO: Add additional optional args to filter search query: type, colour, set, etc.
    #
    # stats_parser.add_argument(
    #     "-s", "--set", help="search database for cards matching this setcode"
    # )
    # stats_parser.add_argument(
    #     "-ct", "--card-type", help="search database for cards matching this type"
    # )

    stats_parser.set_defaults(func=handle_stats)

    # CLEAR ------------------------
    clear_parser = subparsers.add_parser("clear", help="Clear the database")
    clear_parser.set_defaults(func=handle_clear)

    return parser


def handle_random(args):
    if args.number == 1:
        print("Drawing a random card from Scryfall.com...")
    else:
        print(f"Drawing {args.number} random cards from Scryfall.com...")

    query = ""  # TODO: add optional search flag to random argparse

    # get a single random card, based on search parameters
    connection = db_connect()
    card = get_random_card(query) or []
    insert_cards(card, get_timestamp(), connection)
    print(get_total_cards(connection), "cards currently in database.")


def handle_search(args):
    query = " ".join(args.search_query)
    print(f"Searching for cards matching: {query}")

    connection = db_connect()
    card_list = get_card_list(query) or []
    stamp = get_timestamp()
    insert_cards(card_list, stamp, connection)
    print(get_total_cards(connection), "cards currently in database.")
    print(
        f"================================================\nSTATS for '{args.search_query}':"
    )
    print_stats(connection, stamp)


def handle_set(args):
    # Search for a set of cards
    connection = db_connect()

    if args.set_query.lower() == "latest":
        print("Finding the latest set...")
        # TODO: find out how to find the latest set...
    else:
        print(f"Stats for set {args.set_query.upper()}:")

    query = f"set:{args.set_query}"
    card_list = get_card_list(query) or []
    stamp = get_timestamp()
    # HACK: since we know its a set, we could just query sets directly from scryfall?
    insert_cards(card_list, stamp, connection)
    print_stats(connection, stamp)


def handle_setcodes(args):
    print("All main and commander MTG expansions:")

    for set_code in set_codes():
        if set_code[3] == "expansion" or set_code[3] == "commander":
            # extract year from YYYY-MM-DD
            date = datetime.fromisoformat(set_code[2])
            print(
                f"{set_code[0].upper(): <5} {set_code[1]:<40} {set_code[4]:>6} cards {date.year:>10}"
            )


def handle_stats(args):
    print("STATS for ALL cards in database:")
    connection = db_connect()
    print_stats(connection)


def handle_clear(args):
    clear_database()


# Helper functions:


def print_stats(connection, timestamp=None):
    stats = db_stats(connection, timestamp)
    for s in stats:
        print(s)


def get_timestamp():
    return datetime.now()
