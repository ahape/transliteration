from plugins import ALL
from transliterate import FLAVORS, MAPS, LATIN, rubric, transliterate


def test_supermarket_russian():
    assert transliterate("supermarket", "ru", "upper") == "СУПЭРМАРКЭТ"
    assert transliterate("SUPERMARKET", "ru", "lower") == "супэрмаркэт"


def test_hard_and_soft_c():
    assert transliterate("cook", "ru") == "КООК"
    assert transliterate("center", "ru") == "ЦЭНТЭР"
    assert transliterate("centre", "ru")[0] == MAPS["ru"]["C"]
    assert transliterate("civic", "ru") == "ЦИВИК"
    assert transliterate("cook", "el") == "ΚΟΟΚ"
    for lang, table in MAPS.items():
        if FLAVORS[lang].id != "cyrillic":
            continue
        assert transliterate("cook", lang)[0] == table["K"]
        assert transliterate("center", lang)[0] == table["C"]


def test_z_phonetics():
    assert transliterate("zillion", "ru")[0] == MAPS["ru"]["Z"]
    assert transliterate("pizza", "ru") == "ПИЦЦА"
    assert "Ц" in transliterate("pretzel", "ru")
    assert transliterate("pretzel", "ru").count("З") == 0
    assert transliterate("buzz", "ru").endswith("ЗЗ")
    assert transliterate("pizza", "el") == "ΠΙΖΖΑ"


def test_length_without_digraphs():
    assert len(transliterate("window", "uz")) == 6
    assert len(transliterate("jump", "sr")) == 4
    assert len(transliterate("jump", "tg")) == 4


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
    assert transliterate("kitchen", "uk") == "КІТЧЕН"
    assert transliterate("CHAT", "ru", "lower") == "чат"
    assert transliterate("shop", "uk") == "ШОП"
    assert transliterate("chat", "uk") == "ЧАТ"
    assert transliterate("shop", "sr") == "ШОП"
    assert transliterate("chat", "sr") == "ЧАТ"
    assert transliterate("shop", "el") == "ΣΧΟΠ"
    assert transliterate("chat", "el") == "ΤΣΑΤ"


def test_greek_phonetics():
    assert transliterate("supermarket", "el") == "ΣΟΥΠΕΡΜΑΡΚΕΤ"
    assert transliterate("jump", "el") == "ΤΖΟΥΜΠ"
    assert transliterate("this", "el") == "ΘΙΣ"
    assert transliterate("photo", "el") == "ΦΟΤΟ"
    assert transliterate("box", "el") == "ΜΠΟΞ"
    assert transliterate("dog", "el") == "ΝΤΟΓ"
    assert transliterate("center", "el") == "ΣΕΝΤΕΡ"
    assert transliterate("cat", "el") == "ΚΑΤ"
    assert transliterate("code", "el") == "ΚΟΝΤΕ"
    assert transliterate("cold", "el") == "ΚΟΛΝΤ"
    assert transliterate("vase", "el") == "ΒΑΣΕ"
    assert transliterate("base", "el") == "ΜΠΑΣΕ"
    assert transliterate("church", "el") == "ΤΣΟΥΡΤΣ"
    assert MAPS["el"]["B"] == "ΜΠ"
    assert MAPS["el"]["D"] == "ΝΤ"
    assert MAPS["el"]["J"] == "ΤΖ"
    assert MAPS["el"]["U"] == "ΟΥ"
    assert transliterate("bump", "el") == "ΜΠΟΥΜΠ"


def test_maps_cover_a_to_z():
    for lang, table in MAPS.items():
        assert set(table) == set(LATIN), lang
        for glyph in table.values():
            assert glyph, (lang, glyph)


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
    el = rubric("el")
    assert [row["lat"] for row in el[:26]] == list(LATIN)
    assert el[26:] == [
        {"glyph": "Θ", "lat": "TH"},
        {"glyph": "ΤΣ", "lat": "CH"},
        {"glyph": "Φ", "lat": "PH"},
        {"glyph": "Ψ", "lat": "PS"},
    ]
