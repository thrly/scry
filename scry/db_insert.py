import json
from datetime import datetime


def insert_cards(cards: list, timestamp: datetime, connection) -> int:
    try:
        cursor = connection.cursor()
        rows = []
        value_placeholder = "?"
        for card in cards:
            insert_values = transform_card(card, timestamp)
            rows.append(insert_values)
            value_placeholder = ",".join("?" * len(insert_values))
        cursor.executemany(
            f"INSERT OR REPLACE INTO cards VALUES ({value_placeholder})",
            rows,
        )
        connection.commit()
        if len(cards) > 1:
            print(f"Added {len(cards)} cards into database.")
        else:
            print(f"Added '{cards[0]['name']}' into database.")

        return len(cards)
    except Exception as err:
        print(f"Error occured talking to database: {err}")
        return 0


def transform_card(card_data: dict, timestamp: datetime) -> list:
    # TODO: this would be more reliable if it was a dict with named keys, rather than list
    return [
        card_data["id"],
        card_data["name"],
        card_data["type_line"],
        card_data.get("oracle_text", ""),
        json.dumps(card_data.get("color_identity", {})),
        json.dumps(card_data.get("colors", {})),
        card_data.get("set", ""),
        card_data.get("mana_cost", ""),
        card_data["cmc"],
        json.dumps(card_data.get("prices", {})),
        card_data.get("flavor_text", ""),
        timestamp,
    ]
