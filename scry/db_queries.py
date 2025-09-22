import math

from .db import get_connection


# TODO: get db stats for the most recent / current request, and print along with that request
# Could do this by appending a tag for the request when inserting into db, then only querying that tag
# or saving it into a a temp table? (less efficient)?


def db_stats():
    try:
        stats = []

        total_cards = get_total_cards()
        stats.append(f"TOTAL CARDS: {total_cards}")

        connection = get_connection()
        cursor = connection.cursor()

        # Mana Curve of CMC
        cursor.execute("SELECT cmc, COUNT(*) as Mana FROM cards GROUP BY cmc")
        curve = cursor.fetchall()
        stats.append(f"\nMANA CURVE {chart_data(curve, total_cards)}")

        # Tally of card types
        cursor.execute(report_card_types()[0], report_card_types()[1])
        curve = cursor.fetchall()
        stats.append(f"\nCARD TYPES {chart_data(curve, total_cards)}")

        # Prices: highest and average
        stats.append("\nPRICES")
        stats.append(f"Average Price is {report_prices(cursor)[1]} EUR")
        stats.append("\n".join(report_prices(cursor)[0]))

        connection.close()

        return stats

    except Exception as err:
        return ["Error occured talking to database:", {err}]


def get_total_cards():
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(1) FROM cards")
        total_cards = cursor.fetchone()[0]
        connection.close()
        return total_cards
    except Exception as err:
        return ["Error occured talking to database getting Total:", {err}]


def chart_data(curve_data, total_cards):
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


def report_card_types():
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
            GROUP BY w.type
            ORDER BY n DESC;
        """
    return (query, card_types)


def report_prices(cursor):

    cursor.execute(
        "SELECT name, CAST(json_extract(price,'$.eur') AS REAL) AS price FROM cards ORDER BY price DESC LIMIT 3"
    )
    highest_price = cursor.fetchall()
    top_prices = []
    top_prices.append("Most expensive cards:")
    for i, val in enumerate(highest_price):
        top_prices.append(f"  {i+1}. '{val[0]}' at {round(val[1],2)} EUR")

    cursor.execute("SELECT AVG(CAST(json_extract(price,'$.eur') AS REAL)) FROM cards;")
    average_price = cursor.fetchone()[0]
    # stats.append(f"Average price: {round(average_price,2)} EUR")

    return top_prices, round(average_price, 2)
