# Tillwatt

Automated renewable farming. A live, speed-up-able map simulation of a fully automated farm running on renewable energy only. One ledger, sourced part cards, a fence that charges every import.

## Run it
- Play: open `docs/index.html` in a browser (single file, no build step).
- Engine tests: `pip install pytest`, then `pytest`.

## Layout
- `docs/index.html`: the game
- `engine/`: ledger, parts, wear, ruin and weather models
- `tests/`: conservation, ruin and wear tests
- `sources/SOURCES.csv`: where each number comes from
- `DECISIONS.md`, `ROADMAP.md`: why, and what is next

## License
Apache-2.0. See `LICENSE` and `THIRD_PARTY.md`.
