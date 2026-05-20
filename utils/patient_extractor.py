import re
import unicodedata


def extract_patient_name(text: str) -> str:
    for line in (text or "").splitlines():
        cleaned = " ".join(line.split()).strip()
        normalized = _normalize(cleaned)
        match = re.match(r"^(?:para|paciente|nome)\s*(?::|-)?\s*(?P<name>.+)$", normalized, flags=re.IGNORECASE)
        if not match:
            continue

        original_start = match.start("name")
        name = _clean_name(cleaned[original_start:])
        if name:
            return name
    return ""


def _clean_name(value: str) -> str:
    name = value.strip(" .;-")
    normalized = _normalize(name)
    stop_match = re.search(
        r"\s+(?:uso\s+oral|uso\s+continuo|medicamentos?|receita|prescricao)\b",
        normalized,
        flags=re.IGNORECASE,
    )
    if stop_match:
        name = name[: stop_match.start()].strip(" .;-")
    return name


def _normalize(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value or "")
    without_accents = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    return without_accents.lower()
