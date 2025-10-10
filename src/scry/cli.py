import argparse
from datetime import datetime

from scry.db_queries import get_unique_cards
from scry.loading import Loading
from scry.request import find_current_release
from . import (
    get_random_card,
    insert_cards,
    get_card_list,
    db_stats,
    get_total_cards,
    clear_database,
    set_codes,
)


def build_arg_parser() -> argparse.ArgumentParser:
    # setup parser and sub command parsers
    parser = argparse.ArgumentParser(
        description="🃏 Stats for card sets from Scryfall.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            """
    Examples:
        scry setlist
        scry set BLB
        scry set latest
        scry search t:creature c:green legal:modern
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
        help="Arguments as Scryfall-syntax search query (e.g. 't:creature c:green')",
        # TODO: is it possible to set a default value if no query arg is given? 't:land' etc.
    )
    list_parser.set_defaults(func=handle_search)

    # SET ------------------------
    set_parser = subparsers.add_parser("set")
    set_parser.add_argument(
        "set_query",
        help="Specify setcode (run `scry setlist` for reference) or 'latest'",
    )
    set_parser.set_defaults(func=handle_set)

    # SETLIST ------------------------
    setlist_parser = subparsers.add_parser(
        "setlist",
        help="Return list of sets with code, card total, and year of release",
    )
    setlist_parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="Return a full list of set releases including bonus sets, boxes, memorabilia, etc.",
    )
    setlist_parser.set_defaults(func=handle_setlist)

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


################
# Command handlers
#


def handle_random(args, db_connection):
    if args.number == 1:
        print("Drawing a random card from Scryfall.com...")
    else:
        print(f"Drawing {args.number} random cards from Scryfall.com...")

    query = ""  # TODO: add optional search flag to random argparse

    # get a single random card, based on search parameters
    card = get_random_card(query) or []
    insert_cards(card, get_timestamp(), db_connection)
    print(get_total_cards(db_connection), "cards currently in database.")


def handle_search(args, db_connection):
    query = " ".join(args.search_query)
    print(f"Searching for cards matching: {query}")

    card_list = get_card_list(query) or []
    stamp = get_timestamp()
    insert_cards(card_list, stamp, db_connection)
    # print(get_total_cards(db_connection), "cards currently in database.")
    print(f"{len(card_list)} cards found.")
    print_stats(db_connection, stamp)


def handle_set(args, db_connection):
    # Search for a set of cards
    connection = db_connection
    query_setcode = ""
    if args.set_query.lower() == "latest":
        # Find the moce recent release and query stats for it
        current_set = find_current_release(set_codes())
        current_set_code = current_set.get("set_code")
        query_setcode = str(current_set_code)
        current_set_name = current_set.get("name")
        print(f"Stats for {current_set_name} ({current_set_code}):")
    else:
        query_setcode = str(args.set_query)
        print(
            f"Stats for \033[1m{lookup_set_info("name", args.set_query.upper()).upper()}\033[0m"
        )

    query = f"set:{query_setcode}"  # unique:prints includes variations within set, otherwise only unique cards

    card_list = get_card_list(query) or []
    stamp = get_timestamp()

    insert_cards(card_list, stamp, connection)

    # loading animation
    loading = Loading().start()
    set_release_details = []
    set_release_details.append(lookup_set_info("release_date", query_setcode.upper()))
    set_release_details.append(lookup_set_info("card_count", query_setcode.upper()))
    set_release_details.append(get_unique_cards(connection, stamp))
    loading.end()

    print(
        f"""
\x1b[3m  Released: {set_release_details[0]}
  {set_release_details[1]} cards in set
  (Showing {set_release_details[2]} unique cards only)\n \033[0m"""
    )
    print_stats(connection, stamp)


def handle_setlist(args, db_connection):
    if include_all_sets := args.all:
        print("All release sets:", include_all_sets)
    else:
        print("All Main and Commander MTG expansion sets:\n")
    setlist = set_codes(include_all_sets)
    current_set = find_current_release(setlist)
    for set_info in setlist:
        print(
            format_set_info(set_info),
            end="",
        )
        if set_info == current_set:
            print(" <- current release")
        else:
            print()

    print(f"\nShowing {len(setlist)} sets")


def handle_stats(args, db_connection):
    print("STATS for ALL cards in database:")
    print(get_total_cards(db_connection), "cards in database")
    print_stats(db_connection)


def handle_clear(args, db_connection):
    # HACK: why does this only work with db_connection and args, even though neither
    # are required? Same with handle_setlist...
    clear_database()


# Helper functions:


def print_stats(connection, timestamp=None):
    stats = db_stats(connection, timestamp)
    for s in stats:
        print(s)


def format_set_info(set_details) -> str:
    date = datetime.fromisoformat(set_details["release_date"])
    return f"{set_details["set_code"]: <5} {set_details["name"]:<45} {set_details["card_count"]:>6} cards {date.year:>10}"


def lookup_set_info(info: str, set_code: str) -> str:
    setlist = set_codes()
    for s in setlist:
        if set_code == s["set_code"]:
            return s[info]
    return "Set info not found. Check the setcode is correct. You can request name, card_count, release_date"


def get_timestamp():
    return datetime.now()
