# _"scry a card, planeswalker..."_ 🔮🃏

Leveraging [scryfall](https://scryfall.com/docs/api) to get stats for MTG cards

## setup

Clone and install with `pipx install scry`

## use

- Draw a random card and add it to your database with `scry random`
- Get a list of cards based on a scryfall [search query](https://scryfall.com/docs/syntax) and add them to your database:
  - `scry list "set:blb"` returns unique cards from the Bloomburrow set and shows stats for that list.
- Request a list of set releases with: `scry setcodes`
- Return stats for your entire database: `scry stats`
- (Optional:) Clear your database: `scry clear`

## about

Made with python and sqlite, and requests to the [scryfall](https://scryfall.com/docs/api) API.
This is a personal project to learn more about python packaging, sqlite, pytest, and MTG sets.
