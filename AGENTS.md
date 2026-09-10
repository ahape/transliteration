# AGENTS.md

Good code is measured by: conciseness > elegance > breadth of utility > declarative style > everything else.

Prefer the smallest change that works. Do not add an abstraction, framework, or helper until a second use exists. State what is true; skip ceremony.

## Project

Daily 3-word puzzle: English Scrabble words shown as 1:1 Latin-to-Cyrillic ciphers. Flask serves HTML and two JSON endpoints. The browser is vanilla JS + Pico CSS + localStorage. No frontend build.

    app.py              Flask; /api/daily and /api/practice
    transliterate.py    1:1 maps; cipher length equals English length
    generate_puzzles.py seeded calendar; do not rerun unless asked
    static/app.js       game and streak state
    data/*.json         pregenerated words

UTC date from EPOCH 2026-01-01 indexes puzzles.json. Practice words must not overlap scheduled dailies. Version is the `version` field in pyproject.toml.

## Commands

    flask --app app run
    pytest

## Style

- ASCII in comments and docs. Cyrillic belongs in maps and UI.
- Short functions. No types unless they prevent a real bug.
- Server transliterates. Client guesses and stores streaks.
