# add cards to db using scryfall
# query and return stats


from sys import argv
from . import (
    create_table,
    get_random_card,
    insert_cards,
    get_card_list,
    db_stats,
    get_total_cards,
    clear_database,
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
            insert_cards(card)
            print(get_total_cards(), "cards currently in database.")

        elif req_type == "list":
            if len(argv) > 2:
                search_param = argv[2]
                card_list = get_card_list(search_param) or []
                insert_cards(card_list)
                print(get_total_cards(), "cards currently in database.")
            else:
                print("Lists need a query parameter (i.e. 'color:black set:BLB')")

        elif req_type == "clear":
            clear_database()

        elif req_type == "stats":
            stats = db_stats()
            for s in stats:
                print(s)

    else:
        print("No valid search parameters.")


if __name__ == "__main__":
    main()
