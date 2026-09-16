from datetime import datetime, timedelta, timezone

from app import EPOCH, PUZZLES, VERSION, app


def test_index():
    html = app.test_client().get("/").get_data(as_text=True)
    assert "Transliteration" in html
    assert "pico.min.css" in html
    assert f'href="https://github.com/ahape/transliteration/releases/tag/v{VERSION}"' in html
    assert f"v{VERSION}" in html
    assert "Guess the English word behind the Cyrillic." in html
    assert 'value="el"' in html
    assert "Greek" in html
    assert 'id="revealed"' in html
    assert "case-upper" not in html
    assert "practice-nav" not in html


def _assert_daily(data, day):
    assert data["date"] == day.isoformat()
    index = (day - EPOCH).days
    if 0 <= index < len(PUZZLES):
        assert len(data["words"]) == 3
        assert data["words"][0]["cipher"]
        assert data["words"][0]["answer"] in PUZZLES[index]
    else:
        assert data["words"] is None


def test_daily_ok():
    client = app.test_client()
    res = client.get("/api/daily?lang=ru&case=upper")
    assert res.status_code == 200
    data = res.get_json()
    today = datetime.now(timezone.utc).date()
    _assert_daily(data, today)
    assert data["rubric"][0]["lat"] == "A"
    assert data["rubric"][0]["glyph"]
    assert "Cyrillic" in data["tagline"]


def test_daily_uses_client_date():
    now = datetime.now(timezone.utc)
    lo = (now - timedelta(hours=12)).date()
    hi = (now + timedelta(hours=14)).date()
    client = app.test_client()
    for day in {lo, hi, now.date()}:
        res = client.get(f"/api/daily?lang=ru&case=upper&date={day.isoformat()}")
        assert res.status_code == 200
        _assert_daily(res.get_json(), day)


def test_daily_ignores_far_date():
    client = app.test_client()
    res = client.get("/api/daily?lang=ru&case=upper&date=2099-01-01")
    assert res.status_code == 200
    _assert_daily(res.get_json(), datetime.now(timezone.utc).date())


def test_practice_clamps():
    client = app.test_client()
    res = client.get("/api/practice?i=99999&lang=uk&case=lower")
    data = res.get_json()
    assert res.status_code == 200
    assert data["index"] == data["total"] - 1
    assert data["word"]["cipher"] == data["word"]["cipher"].lower()
    assert "Cyrillic" in data["tagline"]


def test_daily_greek():
    client = app.test_client()
    res = client.get("/api/daily?lang=el&case=upper")
    assert res.status_code == 200
    data = res.get_json()
    assert "Greek" in data["tagline"]
    if data["words"]:
        assert data["words"][0]["cipher"]


def test_bad_lang():
    client = app.test_client()
    assert client.get("/api/daily?lang=xx").status_code == 400


def test_runtime_package():
    import scripts.deploy as deploy

    missing = [rel for rel in deploy.RUNTIME_FILES if not (deploy.ROOT / rel).exists()]
    assert missing == []
    assert deploy.version() == VERSION
