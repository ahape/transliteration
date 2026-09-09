from transliterate import MAPS, LATIN, rubric, transliterate


def test_supermarket_russian():
    assert transliterate("supermarket", "ru", "upper") == "СУПЭРМАРКЭТ"
    assert transliterate("SUPERMARKET", "ru", "lower") == "супэрмаркэт"


def test_length_preserved():
    assert len(transliterate("kitchen", "uk")) == 7
    assert len(transliterate("window", "uz")) == 6


def test_maps_cover_a_to_z():
    for lang, table in MAPS.items():
        assert set(table) == set(LATIN), lang
        for glyph in table.values():
            assert len(glyph) == 1, (lang, glyph)


def test_flavors_differ():
    word = "energy"
    rendered = {lang: transliterate(word, lang) for lang in MAPS}
    assert len(set(rendered.values())) > 1


def test_rubric_order():
    rows = rubric("ru")
    assert [row["lat"] for row in rows] == list(LATIN)
    assert rows[0] == {"cyr": "А", "lat": "A"}
