# Transliterillic

A daily three-word puzzle: an English Scrabble word, shown in Cyrillic. New word every day.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flask --app app run
```

> [!NOTE]
> if the default port (`5000`) is occupied, just add `--port 5001` to the end of the `flask` command.

Open http://127.0.0.1:5000

<details>

<summary>
Regenerating the puzzle calendar
</summary>

ENABLE ∩ common English, seeded shuffle:

```bash
python generate_puzzles.py
```

</details>


`pip install pytest` then `pytest` to run the test suite.

