# create SQLITE database and tables, insert into table
import sqlite3
import json


def get_connection():
    return sqlite3.connect("data/cards.db")


def create_table():
    connection = get_connection()
    cursor = connection.cursor()
    schema = """
    CREATE TABLE IF NOT EXISTS cards(
    id TEXT PRIMARY KEY,
    name TEXT,
    type_line TEXT,
    oracle_text TEXT,
    color_identity TEXT,
    colors TEXT,
    set_code TEXT,
    mana_cost TEXT,
    cmc INTEGER, 
    price JSON,
    flavor_text TEXT
    )
    """
    cursor.execute(schema)
    connection.commit()
    connection.close()


def insert_cards(cards):
    try:
        connection = get_connection()
        cursor = connection.cursor()
        rows = []
        for card in cards:
            rows.append(
                (
                    card["id"],
                    card["name"],
                    card["type_line"],
                    card.get("oracle_text", ""),
                    json.dumps(card.get("color_identity", {})),
                    json.dumps(card.get("colors", {})),
                    card.get("set", ""),
                    card.get("mana_cost", ""),
                    card["cmc"],
                    json.dumps(card.get("prices", {})),
                    card.get("flavor_text", ""),
                ),
            )
        # TODO: check if there is a better/more secure way to insert values than '?', which feels insecure. Named variables?
        cursor.executemany(
            "INSERT OR REPLACE INTO cards VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            rows,
        )
        connection.commit()
        connection.close()
        if len(cards) > 1:
            print(f"Added {len(cards)} cards into database.")
        else:
            print(f"Added '{cards[0]['name']}' into database.")

    except Exception as err:
        print(f"Error occured talking to database: {err}")


def clear_database():
    check = input("This will delete your database, are you sure? (y/N): ")
    if check.lower() == "y":
        try:
            connection = get_connection()
            cursor = connection.cursor()
            cursor.execute("DROP TABLE IF EXISTS cards")
            cursor.close()
            print("Database exiled to graveyard and removed from game...")

        except Exception as err:
            print(f"Error clearing database: {err}")
    else:
        print("Damnation avoided.")
