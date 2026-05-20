import re
import unicodedata

from models.medication import REVIEW_LABEL, VALID_PERIODS


def _clean_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value or "")
    without_accents = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    return without_accents.lower().strip()


def normalize_horarios(raw_horarios, posologia_original: str = "") -> list[str]:
    values = []
    if isinstance(raw_horarios, str):
        values = [raw_horarios]
    elif isinstance(raw_horarios, list):
        values = [str(item) for item in raw_horarios if item is not None]

    combined = " ".join(values + [posologia_original or ""])
    text = _clean_text(combined)
    periods: list[str] = []

    if is_any_time_posology(text):
        return []

    for value in values:
        item = _clean_text(value)
        if item in VALID_PERIODS and item not in periods:
            periods.append(item)
        if REVIEW_LABEL in item and REVIEW_LABEL not in periods:
            periods.append(REVIEW_LABEL)

    if "12/12" in text or re.search(r"\b12\s*em\s*12\b", text) or re.search(r"\ba\s*cada\s*12\s*h", text):
        periods = _append(periods, ["cedo", "noite"])
    if "8/8" in text or re.search(r"\b8\s*em\s*8\b", text) or re.search(r"\ba\s*cada\s*8\s*h", text):
        periods = _append(periods, ["cedo", "tarde", "noite"])
    if any(term in text for term in ("pela manha", "de manha", "manha", "ao acordar", "cedo")):
        periods = _append(periods, ["cedo"])
    if any(
        term in text
        for term in (
            "a tarde",
            "pela tarde",
            "tarde",
            "apos almoco",
            "apos o almoco",
            "antes almoco",
            "antes do almoco",
            "depois do almoco",
        )
    ):
        periods = _append(periods, ["tarde"])
    if any(
        term in text
        for term in (
            "a noite",
            "pela noite",
            "noite",
            "ao deitar",
            "antes de dormir",
            "antes jantar",
            "antes do jantar",
            "apos jantar",
            "apos o jantar",
            "depois do jantar",
        )
    ):
        periods = _append(periods, ["noite"])

    recognized = [period for period in periods if period in VALID_PERIODS]
    if recognized:
        return recognized

    return [REVIEW_LABEL]


def is_any_time_posology(value: str) -> bool:
    text = _clean_text(value)
    patterns = (
        r"\b0?1\s*x\s*(?:/|ao\s+)?dia\b",
        r"\b0?1\s+vez\s+(?:ao|por)\s+dia\b",
        r"\buma\s+vez\s+(?:ao|por)\s+dia\b",
        r"\b(?:0?1|um|uma)\s+(?:comprimidos?|comp\.?|capsulas?|caps\.?|gotas?|ml|unidades?|ui)\s+ao\s+dia\b",
    )
    return any(re.search(pattern, text) for pattern in patterns)


def _append(current: list[str], additions: list[str]) -> list[str]:
    for item in additions:
        if item not in current:
            current.append(item)
    return current
