import json
import tomllib
from datetime import date, datetime, timezone
from pathlib import Path

from flask import Flask, jsonify, render_template, request

from transliterate import CASES, LANGS, rubric, transliterate

ROOT = Path(__file__).parent
EPOCH = date(2026, 1, 1)
PUZZLES = json.loads((ROOT / "data" / "puzzles.json").read_text(encoding="utf-8"))
PRACTICE = json.loads((ROOT / "data" / "practice.json").read_text(encoding="utf-8"))


def _load_version():
    with (ROOT / "pyproject.toml").open("rb") as f:
        return tomllib.load(f)["project"]["version"]


VERSION = _load_version()

app = Flask(__name__)
app.json.ensure_ascii = False


def _opts():
    lang = request.args.get("lang", "ru")
    case = request.args.get("case", "upper")
    if lang not in LANGS or case not in CASES:
        return None
    return lang, case


def _pack(word, lang, case):
    return {"cipher": transliterate(word, lang, case), "answer": word}


@app.get("/")
def index():
    return render_template("index.html", version=VERSION)


@app.get("/api/daily")
def daily():
    opts = _opts()
    if opts is None:
        return jsonify({"error": "invalid lang or case"}), 400
    lang, case = opts
    today = datetime.now(timezone.utc).date()
    index = (today - EPOCH).days
    payload = {
        "date": today.isoformat(),
        "index": index,
        "total": len(PUZZLES),
        "rubric": rubric(lang),
        "words": None,
    }
    if 0 <= index < len(PUZZLES):
        payload["words"] = [_pack(word, lang, case) for word in PUZZLES[index]]
    return jsonify(payload)


@app.get("/api/practice")
def practice():
    opts = _opts()
    if opts is None:
        return jsonify({"error": "invalid lang or case"}), 400
    lang, case = opts
    n = len(PRACTICE)
    try:
        i = int(request.args.get("i", 0))
    except ValueError:
        i = 0
    i = max(0, min(i, n - 1)) if n else 0
    word = PRACTICE[i] if n else ""
    return jsonify(
        {
            "index": i,
            "total": n,
            "rubric": rubric(lang),
            "word": _pack(word, lang, case) if n else None,
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
