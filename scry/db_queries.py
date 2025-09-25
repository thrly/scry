import math

from .db import get_connection


# HACK: when a list request is made from scryfall, cards are added to db with that timestamp added
# this timestamp is them used to filter queries from db... this means that cards are always added
# from scryfall before stats are queried, even if they're already in the db.
# PRO: this means the cards are always up to date (and accurate, i.e. in a set query, it means we
# have the full set, rather than a partial that may already exist in db)
# CON: unecessary requests from db, inefficient
# could a different command (local_stats?) check the db WITHOUT using the timestamp method?
# (this would mean redesigning all the db queries...)
#
def db_stats(stamp=None):

    # print("db_status: ", stamp)
    try:
        stats = []

        timestamp_query = ""
        if stamp is not None:
            timestamp_query = f"WHERE added_at = '{stamp}'"

        # print("timestamp_query: ", timestamp_query)
        total_cards = get_total_cards(stamp)
        stats.append(f"Total cards: {total_cards}")

        connection = get_connection()
        cursor = connection.cursor()

        # Mana Curve of CMC
        cursor.execute(
            f"SELECT cmc, COUNT(*) as Mana FROM cards {timestamp_query} GROUP BY cmc"
        )
        curve = cursor.fetchall()
        stats.append(
            f"\nMANA CURVE ============================\n{chart_data(curve, total_cards)}"
        )

        # Tally of card types
        cursor.execute(
            report_card_types(timestamp_query)[0], report_card_types(timestamp_query)[1]
        )
        curve = cursor.fetchall()
        stats.append(
            f"CARD TYPES ============================\n{chart_data(curve, total_cards)}"
        )

        # Prices: highest and average
        stats.append("PRICES ============================\n")
        stats.append(f"Average Price is {report_prices(cursor,timestamp_query)[1]} EUR")
        stats.append("\n".join(report_prices(cursor, timestamp_query)[0]))
        stats.append("\n===========================\n")

        connection.close()

        return stats

    except Exception as err:
        return ["Error occured talking to database:", {err}]


def get_total_cards(timestamp=None):
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            if timestamp is None:
                cursor.execute("SELECT COUNT(1) FROM cards")
            else:
                cursor.execute(
                    "SELECT COUNT(1) FROM cards WHERE added_at = ?", (timestamp,)
                )
            return cursor.fetchone()[0]
    except Exception as err:
        return ["Error occured talking to database getting Total:", {err}]


def chart_data(curve_data, total_cards):
    if total_cards < 1:
        return "Could not chart data. Not enough cards."
    print_curve = "\n"
    percentage_steps = 2  # each block is x%
    scale = 100 / total_cards

    # get longest key as string (just for formatting alignment)
    chart_keys = [str(x) for x, _ in curve_data]
    max_key_string_length = len(max(chart_keys, key=len))

    # scale the bar charts
    for item in curve_data:
        bar = ""
        n_blocks = math.ceil((item[1] * scale) / percentage_steps)
        for _ in range(n_blocks):
            bar += "░"  # ▒█
        # pad out the key to the longest string so the bar charts are aligned
        print_curve += (
            f"  {item[0]:>{max_key_string_length}}: {bar} ({item[1]} cards)\n"
        )
    return print_curve


def report_card_types(timestamp_query=None):
    if timestamp_query is None:
        timestamp_query = ""
    # chart card types based on type_line
    card_types = [
        "Artifact",
        "Creature",
        "Land",
        "Enchantment",
        "Sorcery",
        "Planeswalker",
        "Instant",
        "Legendary",
    ]
    value_placeholder = ",".join(["(?)"] * len(card_types))
    query = f"""
            WITH wanted(type) AS ( VALUES {value_placeholder} )
            SELECT 
                w.type AS bucket,
                COUNT(*) AS n
            FROM wanted w
            JOIN cards c
                ON INSTR(LOWER(COALESCE(c.type_line, '')), TRIM(LOWER(w.type))) > 0
            {timestamp_query}
            GROUP BY w.type
            ORDER BY n DESC;
        """
    return (query, card_types)


def report_prices(cursor, timestamp_query):

    if timestamp_query is None:
        timestamp_query = ""

    cursor.execute(
        f"SELECT name, CAST(json_extract(price,'$.eur') AS REAL) AS price FROM cards {timestamp_query} ORDER BY price DESC LIMIT 3"
    )
    highest_price = cursor.fetchall()
    top_prices = []
    top_prices.append("Most expensive cards:")
    for i, val in enumerate(highest_price):
        top_prices.append(f"  {i+1}. '{val[0]}' at {round(val[1],2)} EUR")

    cursor.execute(
        f"SELECT AVG(CAST(json_extract(price,'$.eur') AS REAL)) FROM cards {timestamp_query}"
    )
    average_price = cursor.fetchone()[0]

    return top_prices, round(average_price, 2)
