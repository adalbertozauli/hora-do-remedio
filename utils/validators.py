import unicodedata

from models.medication import Medication, REVIEW_LABEL
from utils.horario_mapper import is_any_time_posology, normalize_horarios


def validate_medication_item(item: dict) -> Medication:
    medication = Medication(
        medicamento=str(item.get("medicamento") or "").strip(),
        dose=str(item.get("dose") or "").strip(),
        posologia_original=str(item.get("posologia_original") or "").strip(),
        horarios=normalize_horarios(item.get("horarios", []), str(item.get("posologia_original") or "")),
        observacoes=str(item.get("observacoes") or "").strip(),
    )

    if not medication.medicamento:
        medication.medicamento = "Medicamento não identificado"
        medication.observacoes = _join_obs(medication.observacoes, "revisar manualmente: nome do medicamento ausente")
        medication.horarios = [REVIEW_LABEL]

    medication.observacoes = _add_posology_observations(medication.observacoes, medication.posologia_original)

    if is_any_time_posology(medication.posologia_original):
        medication.horarios = []
        medication.observacoes = _remove_obs(medication.observacoes, REVIEW_LABEL)
        medication.observacoes = _join_obs(medication.observacoes, "Qualquer horário")
    elif REVIEW_LABEL in medication.horarios:
        medication.observacoes = _join_obs(medication.observacoes, REVIEW_LABEL)

    return medication


def _add_posology_observations(current: str, posologia: str) -> str:
    text = _clean_text(posologia)
    observations = current

    meal_observations = (
        (("apos o almoco", "apos almoco", "depois do almoco"), "após o almoço"),
        (("antes do almoco", "antes almoco"), "antes do almoço"),
        (("apos o jantar", "apos jantar", "depois do jantar"), "após o jantar"),
        (("antes do jantar", "antes jantar"), "antes do jantar"),
    )
    for terms, label in meal_observations:
        if any(term in text for term in terms):
            observations = _join_obs(observations, label)

    if "em jejum" in text:
        observations = _join_obs(observations, "em jejum")

    return observations


def _clean_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value or "")
    without_accents = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    return without_accents.lower()


def _join_obs(current: str, extra: str) -> str:
    if not current:
        return extra

    current_parts = [_clean_text(part).strip() for part in current.split(";")]
    if _clean_text(extra).strip() in current_parts:
        return current

    return f"{current}; {extra}"


def _remove_obs(current: str, value: str) -> str:
    parts = [part.strip() for part in (current or "").split(";")]
    kept = [part for part in parts if part and _clean_text(part) != _clean_text(value)]
    return "; ".join(kept)
