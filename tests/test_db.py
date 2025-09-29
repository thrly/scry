import sqlite3
import datetime
from scry.db_setup import create_table
from scry.db_insert import insert_cards
from tests.sample_card import sample_card


def test_card_insert_and_get(capfd):

    connection = sqlite3.connect("./tests/tests.db")
    try:
        create_table(connection)

        assert insert_cards([sample_card()], datetime.datetime.now(), connection) == 1
        # this should return 1 (the single card added)

        # check that insert cards writes "Added" message to stdout:
        captured = capfd.readouterr()
        assert captured.out == "Added 'Llanowar Elves' into database.\n"

        # pull first row from test db, then check that it is Llanowar
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM cards")
        card = cursor.fetchone()

        assert card[0] == "6a0b230b-d391-4998-a3f7-7b158a0ec2cd"  # id
        assert card[1] == "Llanowar Elves"  # name
        assert card[2] == "Creature — Elf Druid"  # type_line
        assert card[3] == "{T}: Add {G}."  # oracle_text
        assert card[4] == '["G"]'  # color_identity
        assert card[5] == '["G"]'  # colors
        assert card[6] == "fdn"  # set
        assert card[7] == "{G}"  # mana_cost
        assert card[8] == 1.0  # cmc

    finally:
        connection.close()
