# _"scry a card, planeswalker..."_

a simple test to pull cards from [scryfall](https://scryfall.com/docs/api), using python

## use

1. Add cards into database with a [search query](https://scryfall.com/docs/syntax): `python -m scry list "set:blb"` (returns unique cards from Bloomburrow set) and return stats for that query list.
2. Request a list of set releases with: `python -m scry setcodes`
3. Return stats for entire database: `python -m scry stats`
4. (Optional:) Clear your database: `python -m scry clear`
