"""Build data/puzzles.json and data/practice.json from dolph/dictionary popular.txt.

popular.txt is ENABLE (Scrabble, no proper nouns) intersected with common TV/movie English.
"""

from __future__ import annotations

import json
import random
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent
CACHE = ROOT / ".cache" / "popular.txt"
URL = "https://raw.githubusercontent.com/dolph/dictionary/master/popular.txt"
SEED = 20260101
DAYS = 800
PRACTICE_N = 300
MIN_LEN = 4
MAX_LEN = 10


def load_words() -> list[str]:
    CACHE.parent.mkdir(exist_ok=True)
    if not CACHE.exists():
        req = urllib.request.Request(URL, headers={"User-Agent": "transliterillic"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            CACHE.write_bytes(resp.read())
    words = set()
    for line in CACHE.read_text(encoding="utf-8").splitlines():
        word = line.strip().lower()
        if word.isascii() and word.isalpha() and MIN_LEN <= len(word) <= MAX_LEN:
            words.add(word)
    return sorted(words)


def main() -> None:
    words = load_words()
    need = DAYS * 3 + PRACTICE_N
    if len(words) < need:
        raise SystemExit(f"only {len(words)} eligible words, need {need}")
    rng = random.Random(SEED)
    rng.shuffle(words)
    daily = words[: DAYS * 3]
    practice = words[DAYS * 3 : DAYS * 3 + PRACTICE_N]
    puzzles = [daily[i : i + 3] for i in range(0, DAYS * 3, 3)]

    data = ROOT / "data"
    data.mkdir(exist_ok=True)
    puzzle_lines = ",\n".join(json.dumps(day) for day in puzzles)
    (data / "puzzles.json").write_text("[\n" + puzzle_lines + "\n]\n", encoding="utf-8")
    (data / "practice.json").write_text(
        json.dumps(practice, separators=(",", ":")) + "\n", encoding="utf-8"
    )
    print(f"wrote {DAYS} days and {len(practice)} practice words from {len(words)} eligible")


if __name__ == "__main__":
    main()
