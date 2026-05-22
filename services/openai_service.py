import os

from openai import OpenAI

from services.config_service import load_app_environment, user_env_path


class MissingOpenAIKeyError(RuntimeError):
    pass


SYSTEM_PROMPT = """
Você estrutura receitas médicas para um organizador visual de rotina medicamentosa.
Retorne somente JSON válido, sem markdown e sem explicações.
Não invente horários, medicamentos, doses, indicações clínicas ou instruções ausentes.
Quando houver ambiguidade, texto ilegível, conflito ou falta de horário claro, use "revisar manualmente" em horarios e explique brevemente em observacoes.
Use apenas estes valores em horarios: "cedo", "tarde", "noite", "revisar manualmente".
Regras de conversão seguras:
- "12/12h", "12 em 12 horas" ou equivalente: ["cedo", "noite"].
- "8/8h", "8 em 8 horas" ou equivalente: ["cedo", "tarde", "noite"].
- "pela manhã", "de manhã" ou equivalente: ["cedo"].
- "após o almoço", "após almoço", "depois do almoço" ou equivalente: ["tarde"] e observacoes deve conter "após o almoço".
- "após o jantar", "após jantar", "depois do jantar" ou equivalente: ["noite"] e observacoes deve conter "após o jantar".
- "antes do almoço", "antes almoço" ou equivalente: ["tarde"] e observacoes deve conter "antes do almoço".
- "antes do jantar", "antes jantar" ou equivalente: ["noite"] e observacoes deve conter "antes do jantar".
- Quando houver "em jejum", observacoes deve conter "em jejum".
- Para insulinas ou medicações em unidades, use a dose do período como "10 UI", "20 UI" etc. quando o texto disser "10 unidades", "20 unidades" ou equivalente.
- Quando houver "01 comprimido ao dia", "1x ao dia", "1x/dia", "uma vez ao dia" ou termo similar sem período específico, use horarios: [] e observacoes deve conter "Qualquer horário".
- "à noite", "ao deitar", "antes de dormir" ou equivalente: ["noite"].
- Se a posologia não deixar o horário claro: ["revisar manualmente"].
Formato obrigatório:
[
  {
    "medicamento": "nome",
    "dose": "dose ou vazio",
    "posologia_original": "texto original da orientação",
    "horarios": ["cedo"],
    "observacoes": ""
  }
]
""".strip()


def structure_prescription_text(text: str) -> str:
    load_app_environment()
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise MissingOpenAIKeyError(
            "O texto da receita foi extraído, mas a tabela automática precisa da chave da OpenAI.\n\n"
            "Clique em 'Configurar chave da API' no aplicativo ou crie o arquivo:\n"
            f"{user_env_path()}\n\n"
            "com a linha OPENAI_API_KEY=sua_chave_aqui."
        )

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini"
    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model=model,
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    "Extraia as medicações da receita abaixo. "
                    "Responda somente com o JSON no formato solicitado.\n\n"
                    f"{text}"
                ),
            },
        ],
    )

    return response.choices[0].message.content or ""
