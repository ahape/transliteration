# Transliterillic

A daily three-word puzzle: an English Scrabble word, shown in Cyrillic. Same UTC date, same three words for everyone.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flask --app app run
```

Open http://127.0.0.1:5000

To regenerate the puzzle calendar (ENABLE ∩ common English, seeded shuffle):

```bash
python generate_puzzles.py
```

`pip install pytest` then `pytest` for the small unit tests.
