# add cards to db using scryfall
# query and return stats


from datetime import datetime
from sys import argv
from . import (
    create_table,
    get_random_card,
    insert_cards,
    get_card_list,
    db_stats,
    get_total_cards,
    clear_database,
    set_codes,
)


def main():
    create_table()
    if len(argv) > 1:
        req_type = argv[1]
        # use argument inputs from CLI: random (single card) or list (multiple cards)
        if req_type == "random":
            # optional query argument for random card, otherwise no constraint
            if 1 < len(argv) > 2:
                query = argv[1]
            else:
                query = ""
            # get a single random card, based on search parameters
            card = get_random_card(query) or []
            insert_cards(card, get_timestamp())
            print(get_total_cards(), "cards currently in database.")

        elif req_type == "list":
            if len(argv) > 2:
                search_param = argv[2]
                card_list = get_card_list(search_param) or []
                stamp = get_timestamp()
                insert_cards(card_list, stamp)
                print(get_total_cards(), "cards currently in database.")
                print(
                    f"================================================\nSTATS for '{search_param}':"
                )
                print_stats(stamp)

            else:
                print("Lists need a query parameter (i.e. 'color:black set:BLB')")

        elif req_type == "setcodes":
            for set_code in set_codes():
                if set_code[3] == "expansion" or set_code[3] == "commander":
                    # extract year from YYYY-MM-DD
                    date = datetime.fromisoformat(set_code[2])
                    print(
                        f"{set_code[0]} : {set_code[1]}\t{set_code[4]} cards\t({date.year})"
                    )
        elif req_type == "clear":
            clear_database()

        elif req_type == "stats":
            print(
                "================================================\nSTATS for ALL cards in database:"
            )
            print_stats()
    else:
        print("No valid search parameters.")


def print_stats(timestamp=None):
    stats = db_stats(timestamp)
    for s in stats:
        print(s)


def get_timestamp():
    return datetime.now()


if __name__ == "__main__":
    main()
