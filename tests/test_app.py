from datetime import datetime, timezone

from app import EPOCH, PUZZLES, app


def test_index():
    html = app.test_client().get("/").get_data(as_text=True)
    assert "Transliterillic" in html
    assert "pico.min.css" in html


def test_daily_ok():
    client = app.test_client()
    res = client.get("/api/daily?lang=ru&case=upper")
    assert res.status_code == 200
    data = res.get_json()
    today = datetime.now(timezone.utc).date()
    assert data["date"] == today.isoformat()
    index = (today - EPOCH).days
    if 0 <= index < len(PUZZLES):
        assert len(data["words"]) == 3
        assert data["words"][0]["cipher"]
        assert data["words"][0]["answer"] in PUZZLES[index]
    else:
        assert data["words"] is None
    assert data["rubric"][0]["lat"] == "A"


def test_practice_clamps():
    client = app.test_client()
    res = client.get("/api/practice?i=99999&lang=uk&case=lower")
    data = res.get_json()
    assert res.status_code == 200
    assert data["index"] == data["total"] - 1
    assert data["word"]["cipher"] == data["word"]["cipher"].lower()


def test_bad_lang():
    client = app.test_client()
    assert client.get("/api/daily?lang=xx").status_code == 400
