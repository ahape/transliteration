"""Latin→script engine. Letters are 1:1; plugins may add digraphs."""

from plugins import ALL

CASES = ("upper", "lower")
LATIN = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

FLAVORS = {}
MAPS = {}
DIGRAPHS = {}
for plugin in ALL:
    extra = getattr(plugin, "digraphs", {})
    for code, (_, glyphs) in plugin.flavors.items():
        if len(glyphs) != len(LATIN):
            raise ValueError(f"{plugin.id}:{code} has {len(glyphs)} glyphs, need {len(LATIN)}")
        FLAVORS[code] = plugin
        MAPS[code] = dict(zip(LATIN, glyphs))
        DIGRAPHS[code] = extra

LANGS = tuple(MAPS)
DEFAULT_LANG = LANGS[0]

_SOFT = set("EIY")
_TS_Z = frozenset({"PIZZA", "PIZZAS", "PIAZZA", "PAPARAZZI"})
_HARD_C_EXCEPTIONS = frozenset({"SOCCER", "SICCED"})


def _fold_phonetics(word, lang):
    """Hard C->K; Cyrillic /ts/ Z->C. word is uppercase."""
    cyr = FLAVORS[lang].id == "cyrillic"
    out = []
    for i, ch in enumerate(word):
        nxt = word[i + 1] if i + 1 < len(word) else ""
        prev = word[i - 1] if i else ""
        if ch == "C" and nxt != "H" and (nxt not in _SOFT or word in _HARD_C_EXCEPTIONS):
            out.append("K")
        elif cyr and ch == "Z" and (prev == "T" or word in _TS_Z):
            out.append("C")
        else:
            out.append(ch)
    return "".join(out)


def transliterate(word, lang=DEFAULT_LANG, case="upper"):
    if lang not in MAPS:
        raise ValueError(f"unknown lang: {lang}")
    if case not in CASES:
        raise ValueError(f"unknown case: {case}")
    table = MAPS[lang]
    extras = DIGRAPHS[lang]
    text = _fold_phonetics(word.upper(), lang)
    out = []
    i = 0
    try:
        while i < len(text):
            pair = text[i : i + 2]
            if pair in extras:
                out.append(extras[pair])
                i += 2
            else:
                out.append(table[text[i]])
                i += 1
    except KeyError as e:
        raise ValueError(f"unmapped character: {e.args[0]!r}") from None
    cipher = "".join(out)
    return cipher.lower() if case == "lower" else cipher


def rubric(lang=DEFAULT_LANG):
    if lang not in MAPS:
        raise ValueError(f"unknown lang: {lang}")
    rows = [{"glyph": MAPS[lang][l], "lat": l} for l in LATIN]
    rows.extend({"glyph": g, "lat": lat} for lat, g in DIGRAPHS[lang].items())
    return rows
