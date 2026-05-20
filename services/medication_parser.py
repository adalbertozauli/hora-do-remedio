import json

from models.medication import Medication
from utils.validators import validate_medication_item


def parse_medications_json(raw_json: str) -> list[Medication]:
    data = json.loads(_strip_markdown(raw_json))
    if not isinstance(data, list):
        raise ValueError("A resposta da IA não está no formato esperado de lista JSON.")

    medications: list[Medication] = []
    for item in data:
        if not isinstance(item, dict):
            raise ValueError("A resposta da IA contém um item inválido.")
        medications.append(validate_medication_item(item))

    return medications


def medications_to_json(medications: list[Medication]) -> str:
    return json.dumps([item.to_dict() for item in medications], ensure_ascii=False, indent=2)


def _strip_markdown(value: str) -> str:
    text = (value or "").strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return text
