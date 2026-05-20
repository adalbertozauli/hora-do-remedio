import re
import unicodedata
from dataclasses import dataclass, field


VALID_PERIODS = ("cedo", "tarde", "noite")
REVIEW_LABEL = "revisar manualmente"


@dataclass
class Medication:
    medicamento: str = ""
    dose: str = ""
    posologia_original: str = ""
    horarios: list[str] = field(default_factory=list)
    observacoes: str = ""
    period_doses: dict[str, str] = field(default_factory=dict)

    @property
    def needs_review(self) -> bool:
        return REVIEW_LABEL in self.horarios or REVIEW_LABEL in self.observacoes.lower()

    def period_text(self, period: str) -> str:
        if period not in self.horarios:
            return ""
        if self.period_doses.get(period):
            return self.period_doses[period]
        return extract_administration_amount_for_period(self.posologia_original, period) or extract_administration_amount(self.posologia_original) or "revisar"

    def to_dict(self) -> dict:
        return {
            "medicamento": self.medicamento,
            "dose": self.dose,
            "posologia_original": self.posologia_original,
            "horarios": self.horarios,
            "observacoes": self.observacoes,
        }


def extract_administration_amount(posologia: str) -> str:
    text = _normalize(posologia)
    pattern = _amount_pattern()
    match = pattern.search(text)
    if not match:
        return ""

    amount = _amount_label(match.group("amount"))
    form = _form_label(match.group("form"), amount)
    return f"{amount} {form}"


def extract_administration_amount_for_period(posologia: str, period: str) -> str:
    text = _normalize(posologia)
    matches = list(_amount_pattern().finditer(text))
    if len(matches) < 2:
        return ""

    terms = _period_terms(period)
    for index, match in enumerate(matches):
        next_start = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        segment_after = text[match.end() : next_start]
        segment_before = text[matches[index - 1].end() if index > 0 else 0 : match.start()]
        if any(term in segment_after or term in segment_before for term in terms):
            amount = _amount_label(match.group("amount"))
            form = _form_label(match.group("form"), amount)
            return f"{amount} {form}"

    return ""


def _amount_pattern() -> re.Pattern:
    return re.compile(
        r"\b(?P<amount>\d{1,2}|um|uma|dois|duas|meio|meia)\s+"
        r"(?P<form>comprimidos?|comp\.?|capsulas?|caps\.?|gotas?|ml|mililitros?|saches?|envelopes?|unidades?|ui|u\.i\.?)\b"
    )


def _period_terms(period: str) -> tuple[str, ...]:
    if period == "cedo":
        return ("cedo", "manha", "ao acordar", "cafe da manha")
    if period == "tarde":
        return ("tarde", "almoco", "apos almoco", "antes do almoco", "antes almoco")
    if period == "noite":
        return ("noite", "jantar", "deitar", "dormir")
    return ()


def _normalize(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value or "")
    without_accents = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    return without_accents.lower()


def _amount_label(value: str) -> str:
    words = {
        "um": "01",
        "uma": "01",
        "dois": "02",
        "duas": "02",
        "meio": "1/2",
        "meia": "1/2",
    }
    if value in words:
        return words[value]
    if value.isdigit() and len(value) == 1:
        return f"0{value}"
    return value


def _form_label(value: str, amount: str) -> str:
    if value.startswith("comp"):
        return "comp."
    if value.startswith("caps"):
        return "caps."
    if value.startswith("gota"):
        return "gota" if amount in ("01", "1/2") else "gotas"
    if value in ("ml", "mililitro", "mililitros"):
        return "ml"
    if value.startswith("sache"):
        return "sachê" if amount in ("01", "1/2") else "sachês"
    if value.startswith("envelope"):
        return "env." if amount in ("01", "1/2") else "envs."
    if value in ("unidade", "unidades", "ui", "u.i", "u.i."):
        return "UI"
    return value
