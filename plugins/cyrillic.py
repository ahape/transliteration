"""Cyrillic 1:1 maps by language flavor, plus SH->sha and CH->che."""

id = "cyrillic"
label = "Cyrillic"
tagline = "Guess the English word behind the Cyrillic."
flavors = {
    "ru": ("Russian", "АБЦДЭФГХИЖКЛМНОПКРСТУВВХЙЗ"),
    "uk": ("Ukrainian", "АБЦДЕФҐГІЖКЛМНОПКРСТУВВХИЗ"),
    "sr": ("Serbian", "АБЦДЕФГХИЏКЛМНОПКРСТУВВХЈЗ"),
    "uz": ("Uzbek", "АБЦДЕФГҲИЖКЛМНОПҚРСТУВЎХЙЗ"),
    "tg": ("Tajik", "АБЦДЕФГҲИҶКЛМНОПҚРСТУВВХЙЗ"),
}
digraphs = {"CH": "Ч", "SH": "Ш"}
