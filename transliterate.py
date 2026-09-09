"""1:1 Latin→Cyrillic maps. Cipher length always equals English length."""

CASES = ("upper", "lower")
LATIN = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

CYRILLIC_STRINGS = {
    "ru": "АБЦДЭФГХИЖКЛМНОПКРСТУВВХЙЗ",
    "uk": "АБЦДЕФҐГІЖКЛМНОПКРСТУВВХИЗ",
    "uz": "АБЦДЕФГҲИЖКЛМНОПҚРСТУВЎХЙЗ",
    "sr": "АБЦДЕФГХИЏКЛМНОПКРСТУВВХЈЗ",
    "tg": "АБЦДЕФГҲИҶКЛМНОПҚРСТУВВХЙЗ",
}

MAPS = {lang: dict(zip(LATIN, chars)) for lang, chars in CYRILLIC_STRINGS.items()}
LANGS = tuple(MAPS)


def transliterate(word, lang="ru", case="upper"):
    if lang not in MAPS:
        raise ValueError(f"unknown lang: {lang}")
    if case not in CASES:
        raise ValueError(f"unknown case: {case}")
    table = MAPS[lang]
    try:
        cipher = "".join(table[ch] for ch in word.upper())
    except KeyError as e:
        raise ValueError(f"unmapped character: {e.args[0]!r}") from None
    return cipher.lower() if case == "lower" else cipher


def rubric(lang="ru"):
    """Latin A–Z rows: {cyr, lat}. Duplicate glyphs are allowed."""
    if lang not in CYRILLIC_STRINGS:
        raise ValueError(f"unknown lang: {lang}")
    return [{"cyr": c, "lat": l} for l, c in zip(LATIN, CYRILLIC_STRINGS[lang])]
