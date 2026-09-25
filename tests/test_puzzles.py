import json
import re
from collections import Counter
from datetime import date
from pathlib import Path

from transliterate import transliterate

ROOT = Path(__file__).resolve().parents[1]
WORD = re.compile(r"^[a-z]{4,10}$")


def test_calendar_shape():
    puzzles = json.loads((ROOT / "data" / "puzzles.json").read_text(encoding="utf-8"))
    practice = json.loads((ROOT / "data" / "practice.json").read_text(encoding="utf-8"))
    assert len(puzzles) == 800
    assert all(len(day) == 3 for day in puzzles)
    daily = [word for day in puzzles for word in day]
    assert all(WORD.match(word) for word in daily)
    assert all(WORD.match(word) for word in practice)
    assert len(daily) == len(set(daily))
    assert len(practice) > 10000
    assert set(daily).isdisjoint(practice)


def test_greek_ciphers_are_unique():
    puzzles = json.loads((ROOT / "data" / "puzzles.json").read_text(encoding="utf-8"))
    practice = json.loads((ROOT / "data" / "practice.json").read_text(encoding="utf-8"))
    words = [word for day in puzzles for word in day] + practice
    counts = Counter(transliterate(word, "el") for word in words)
    assert [cipher for cipher, n in counts.items() if n > 1] == []


def test_epoch_index():
    assert (date(2026, 1, 1) - date(2026, 1, 1)).days == 0
    assert (date(2026, 9, 9) - date(2026, 1, 1)).days == 251
