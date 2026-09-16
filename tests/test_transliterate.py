from plugins import ALL
from transliterate import MAPS, LATIN, rubric, transliterate


def test_supermarket_russian():
    assert transliterate("supermarket", "ru", "upper") == "СУПЭРМАРКЭТ"
    assert transliterate("SUPERMARKET", "ru", "lower") == "супэрмаркэт"


def test_length_preserved():
    assert len(transliterate("market", "uk")) == 6
    assert len(transliterate("window", "uz")) == 6
    assert len(transliterate("jump", "sr")) == 4
    assert len(transliterate("jump", "tg")) == 4
    assert len(transliterate("kitchen", "el")) == 7


def test_serbian_and_tajik_letters():
    assert transliterate("jump", "sr") == "ЏУМП"
    assert transliterate("yes", "sr") == "ЈЕС"
    assert transliterate("jump", "tg") == "ҶУМП"
    assert transliterate("qosh", "tg") == "ҚОШ"


def test_cyrillic_digraphs():
    assert transliterate("shop", "ru") == "ШОП"
    assert transliterate("fish", "ru") == "ФИШ"
    assert transliterate("hush", "ru") == "ХУШ"
    assert transliterate("sssh", "ru") == "ССШ"
    assert transliterate("SHOP", "ru", "lower") == "шоп"
    assert transliterate("chat", "ru") == "ЧАТ"
    assert transliterate("church", "ru") == "ЧУРЧ"
    assert transliterate("rich", "ru") == "РИЧ"
    assert transliterate("match", "ru") == "МАТЧ"
    assert transliterate("CHAT", "ru", "lower") == "чат"
    assert transliterate("shop", "uk") == "ШОП"
    assert transliterate("chat", "uk") == "ЧАТ"
    assert transliterate("shop", "sr") == "ШОП"
    assert transliterate("chat", "sr") == "ЧАТ"
    assert transliterate("shop", "el") == "ΣΗΟΠ"
    assert transliterate("chat", "el") == "ΞΗΑΤ"


def test_greek_supermarket():
    assert transliterate("supermarket", "el") == "ΣΥΠΕΡΜΑΡΚΕΤ"
    assert transliterate("jump", "el") == "ΙΥΜΠ"


def test_maps_cover_a_to_z():
    for lang, table in MAPS.items():
        assert set(table) == set(LATIN), lang
        for glyph in table.values():
            assert len(glyph) == 1, (lang, glyph)


def test_plugins():
    codes = []
    for plugin in ALL:
        assert plugin.id and plugin.label and plugin.tagline
        for code, (name, glyphs) in plugin.flavors.items():
            assert name and len(glyphs) == len(LATIN)
            codes.append(code)
    assert len(codes) == len(set(codes))
    assert "ru" in codes and "el" in codes


def test_flavors_differ():
    word = "energy"
    rendered = {lang: transliterate(word, lang) for lang in MAPS}
    assert len(set(rendered.values())) > 1


def test_rubric_order():
    rows = rubric("ru")
    assert [row["lat"] for row in rows[:26]] == list(LATIN)
    assert rows[0] == {"glyph": "А", "lat": "A"}
    assert [row["lat"] for row in rows[26:]] == ["CH", "SH"]
    assert rows[-2:] == [{"glyph": "Ч", "lat": "CH"}, {"glyph": "Ш", "lat": "SH"}]
    assert [row["lat"] for row in rubric("el")] == list(LATIN)
