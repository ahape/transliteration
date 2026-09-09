# Transliterillic

A daily three-word puzzle: an English Scrabble word, shown in Cyrillic. Same UTC date, same three words for everyone.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flask --app app run
```

> [!NOTE]
> if the default port (`5000`) is occupied, just add `--port 5001` to the end of the `flask` command.

Open http://127.0.0.1:5000

To regenerate the puzzle calendar (ENABLE ∩ common English, seeded shuffle):

```bash
python generate_puzzles.py
```

Version is the `version` field in `pyproject.toml`.

`pip install pytest` then `pytest` for the small unit tests.
