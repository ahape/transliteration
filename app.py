import json
import tomllib
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_from_directory

from transliterate import ALL, CASES, DEFAULT_LANG, FLAVORS, rubric, transliterate

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
    lang = request.args.get("lang", DEFAULT_LANG)
    case = request.args.get("case", "upper")
    if lang not in FLAVORS or case not in CASES:
        return None
    return lang, case


def _pack(word, lang, case):
    return {"cipher": transliterate(word, lang, case), "answer": word}


def _today():
    now = datetime.now(timezone.utc)
    raw = request.args.get("date")
    if raw:
        try:
            wanted = date.fromisoformat(raw)
        except ValueError:
            wanted = None
        else:
            lo = (now - timedelta(hours=12)).date()
            hi = (now + timedelta(hours=14)).date()
            if lo <= wanted <= hi:
                return wanted
    return now.date()


@app.get("/favicon.ico")
def favicon():
    return send_from_directory(app.static_folder, "favicon.ico")


@app.get("/")
def index():
    return render_template(
        "index.html",
        version=VERSION,
        plugins=ALL,
        tagline=ALL[0].tagline,
    )


@app.get("/api/daily")
def daily():
    opts = _opts()
    if opts is None:
        return jsonify({"error": "invalid lang or case"}), 400
    lang, case = opts
    today = _today()
    index = (today - EPOCH).days
    payload = {
        "date": today.isoformat(),
        "index": index,
        "total": len(PUZZLES),
        "tagline": FLAVORS[lang].tagline,
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
            "tagline": FLAVORS[lang].tagline,
            "rubric": rubric(lang),
            "word": _pack(word, lang, case) if n else None,
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
