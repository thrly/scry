import requests
from time import sleep
import urllib.parse


url = "https://api.scryfall.com"
headers = {"User-Agent": "scry-thrly/0.1", "Accept": "*/*"}

# NOTE: scryfall returns an 'object : card/list` which could be used to detemine how to display/add single/lists of cards


def get_random_card(query):
    clean_query = urllib.parse.quote(query)
    endpoint = "/cards/random/?q="

    try:
        res = requests.get(url + endpoint + clean_query, headers=headers, timeout=3)
        res.raise_for_status()

        card = res.json()

        warnings = card.get("warnings")
        if warnings:
            print(f"WARNING [RANDOM REQ]: {warnings}")

        if res.status_code == 200:
            print(
                # prints name in bold, type in italics
                f"Drew card: \033[1m{card['name']}\033[0m : \x1b[3m{card['type_line']}\x1b[0m from {card['set_name']} {card['color_identity']}"
            )
            print(f"{card['type_line']}")
            return [card]
        else:
            print("Something may have gone wrong... Status Code: ", res.status_code)
            return []
    except requests.exceptions.RequestException as err:
        print("ERROR: ", err)


def get_card_list(query):
    clean_query = urllib.parse.quote(query)
    endpoint = "/cards/search?q="

    sleep(0.1)  # just in case we ever call this in a loop

    try:
        req_url = url + endpoint + clean_query
        # print(f"Requesting from: {req_url}")
        res = requests.get(req_url, headers=headers, timeout=3)
        res.raise_for_status()

        page_one = res.json()
        # print(f"Search returned {page_one.get("total_cards", 0)} cards.")

        show_warnings(page_one)

        # If there are additional pages (has_more) keep requesting from the "next_page" url
        # Add subsequent results ("data") values into the card list

        is_paginated = page_one.get("has_more")
        next_page = page_one.get("next_page")

        card_list = page_one.get("data")

        while is_paginated:
            try:
                sleep(0.11)  # just in case we ever call this in a loop

                additional_res = requests.get(next_page, headers=headers, timeout=3)
                additional_res.raise_for_status()
                new_page_results = additional_res.json()

                show_warnings(new_page_results)

                # add new results page items into card_list
                for i in new_page_results.get("data"):
                    card_list.append(i)

                # set values for next page if required
                is_paginated = new_page_results.get("has_more")
                next_page = new_page_results.get("next_page")

            except requests.exceptions.RequestException as err:
                print("ERROR subsequent pages: ", err)

        if res.status_code == 200:
            return card_list
        else:
            print("Something may have gone wrong... Status Code: ", res.status_code)
            return []
    except requests.exceptions.RequestException as err:
        print("ERROR: ", err)


def show_warnings(res):
    warnings = res.get("warnings")
    if warnings:
        print(f"WARNING [LIST REQ]: {warnings}")


def set_codes():
    endpoint = "/sets"

    sleep(0.1)  # just in case we ever call this in a loop

    try:
        req_url = url + endpoint
        res = requests.get(req_url, headers=headers, timeout=3)
        res.raise_for_status()

        if res.status_code == 200:
            response = res.json()

            show_warnings(response)

            setlist_data = response.get("data", [])

            setlist = []
            for set_item in setlist_data:
                setlist.append(
                    [
                        set_item.get("code").upper(),
                        set_item.get("name"),
                        set_item.get("released_at"),
                        set_item.get("set_type"),
                        set_item.get("card_count"),
                    ]
                )
            print(type(setlist))
            return setlist

        else:
            print("Something may have gone wrong... Status Code: ", res.status_code)
            return []

    except requests.exceptions.RequestException as err:
        print("Setlist ERROR: ", err)
        return []
