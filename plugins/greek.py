"""Phonetic Modern Greek. C maps to sigma; hard C is folded to K before lookup."""

id = "greek"
label = "Greek"
tagline = "Guess the English word behind the Greek."
_EL = (
    "Α", "ΜΠ", "Σ", "ΝΤ", "Ε", "Φ", "Γ", "Χ", "Ι", "ΤΖ",
    "Κ", "Λ", "Μ", "Ν", "Ο", "Π", "Κ", "Ρ", "Σ", "Τ",
    "ΟΥ", "Β", "ΟΥ", "Ξ", "Υ", "Ζ",
)
flavors = {"el": ("Modern", _EL)}
digraphs = {"TH": "Θ", "CH": "ΤΣ", "PH": "Φ", "PS": "Ψ"}
