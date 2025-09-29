# test the clean-up/transofrm of card data ready for inserting into

import datetime
from scry.db_insert import transform_card
from tests.sample_card import sample_card


def test_transform_card_pulls_correct_values():

    card = transform_card(sample_card(), datetime.datetime.now())

    assert card[0] == "6a0b230b-d391-4998-a3f7-7b158a0ec2cd"  # id
    assert card[1] == "Llanowar Elves"  # name
    assert card[2] == "Creature — Elf Druid"  # type_line
    assert card[3] == "{T}: Add {G}."  # oracle_text
    assert card[4] == '["G"]'  # color_identity
    assert card[5] == '["G"]'  # colors
    assert card[6] == "fdn"  # set
    assert card[7] == "{G}"  # mana_cost
    assert card[8] == 1.0  # cmc
    # TODO: assertion to check prices
    assert (
        card[9]
        == '{"usd": "0.23", "usd_foil": "3.20", "usd_etched": null, "eur": "0.22", "eur_foil": "0.37", "tix": "0.03"}'
    )  # prices
    assert (
        card[10]
        == "The elves of the Llanowar forest have defended it for generations. It is their sacred duty to keep outside influences from corrupting their ancestral home."
    )  # flavor_text
    assert type(card[11]) is datetime.datetime  # timestamp
