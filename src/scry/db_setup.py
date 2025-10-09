# create SQLITE database and tables, insert into table
import sqlite3
from pathlib import Path
from os import makedirs

# set path (if required) for db: scry/data/cards.db
path_to_root = Path(__file__).parent.parent.parent  # project root scry/
makedirs(path_to_root / "data/", exist_ok=True)


def db_connect():
    return sqlite3.connect(Path(path_to_root / "data" / "cards.db"))


def create_table(connection):
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
    flavor_text TEXT,
    rarity TEXT,
    added_at TEXT 
    )
    """
    cursor.execute(schema)
    connection.commit()


def clear_database() -> None:
    check = input("This will delete your database, are you sure? (y/N): ")
    if check.lower() == "y":
        try:
            connection = db_connect()
            cursor = connection.cursor()
            cursor.execute("DROP TABLE IF EXISTS cards")
            cursor.close()
            print("Database exiled to graveyard and removed from game...")

        except Exception as err:
            print(f"Error clearing database: {err}")
    else:
        print("Damnation avoided.")
