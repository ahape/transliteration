"""1:1 Latin→Cyrillic maps. Cipher length always equals English length."""

CASES = ("upper", "lower")
LATIN = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

MAPS = {
    "ru": {
        "A": "А",
        "B": "Б",
        "C": "Ц",
        "D": "Д",
        "E": "Э",
        "F": "Ф",
        "G": "Г",
        "H": "Х",
        "I": "И",
        "J": "Ж",
        "K": "К",
        "L": "Л",
        "M": "М",
        "N": "Н",
        "O": "О",
        "P": "П",
        "Q": "К",
        "R": "Р",
        "S": "С",
        "T": "Т",
        "U": "У",
        "V": "В",
        "W": "В",
        "X": "Х",
        "Y": "Й",
        "Z": "З",
    },
    "uk": {
        "A": "А",
        "B": "Б",
        "C": "Ц",
        "D": "Д",
        "E": "Е",
        "F": "Ф",
        "G": "Ґ",
        "H": "Г",
        "I": "І",
        "J": "Ж",
        "K": "К",
        "L": "Л",
        "M": "М",
        "N": "Н",
        "O": "О",
        "P": "П",
        "Q": "К",
        "R": "Р",
        "S": "С",
        "T": "Т",
        "U": "У",
        "V": "В",
        "W": "В",
        "X": "Х",
        "Y": "И",
        "Z": "З",
    },
    "uz": {
        "A": "А",
        "B": "Б",
        "C": "Ц",
        "D": "Д",
        "E": "Е",
        "F": "Ф",
        "G": "Г",
        "H": "Ҳ",
        "I": "И",
        "J": "Ж",
        "K": "К",
        "L": "Л",
        "M": "М",
        "N": "Н",
        "O": "О",
        "P": "П",
        "Q": "Қ",
        "R": "Р",
        "S": "С",
        "T": "Т",
        "U": "У",
        "V": "В",
        "W": "Ў",
        "X": "Х",
        "Y": "Й",
        "Z": "З",
    },
    "sr": {
        "A": "А",
        "B": "Б",
        "C": "Ц",
        "D": "Д",
        "E": "Е",
        "F": "Ф",
        "G": "Г",
        "H": "Х",
        "I": "И",
        "J": "Џ",
        "K": "К",
        "L": "Л",
        "M": "М",
        "N": "Н",
        "O": "О",
        "P": "П",
        "Q": "К",
        "R": "Р",
        "S": "С",
        "T": "Т",
        "U": "У",
        "V": "В",
        "W": "В",
        "X": "Х",
        "Y": "Ј",
        "Z": "З",
    },
    "tg": {
        "A": "А",
        "B": "Б",
        "C": "Ц",
        "D": "Д",
        "E": "Е",
        "F": "Ф",
        "G": "Г",
        "H": "Ҳ",
        "I": "И",
        "J": "Ҷ",
        "K": "К",
        "L": "Л",
        "M": "М",
        "N": "Н",
        "O": "О",
        "P": "П",
        "Q": "Қ",
        "R": "Р",
        "S": "С",
        "T": "Т",
        "U": "У",
        "V": "В",
        "W": "В",
        "X": "Х",
        "Y": "Й",
        "Z": "З",
    },
}

LANGS = tuple(MAPS)


def transliterate(word, lang="ru", case="upper"):
    if lang not in MAPS:
        raise ValueError(f"unknown lang: {lang}")
    if case not in CASES:
        raise ValueError(f"unknown case: {case}")
    table = MAPS[lang]
    out = []
    for ch in word.upper():
        mapped = table.get(ch)
        if mapped is None:
            raise ValueError(f"unmapped character: {ch!r}")
        out.append(mapped)
    cipher = "".join(out)
    return cipher.lower() if case == "lower" else cipher


def rubric(lang="ru"):
    """Latin A–Z rows: {cyr, lat}. Duplicate glyphs are allowed."""
    if lang not in MAPS:
        raise ValueError(f"unknown lang: {lang}")
    table = MAPS[lang]
    return [{"cyr": table[letter], "lat": letter} for letter in LATIN]
