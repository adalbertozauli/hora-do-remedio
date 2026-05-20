# Hora do Remédio

Aplicativo desktop para Windows que importa receitas médicas em `.docx`, extrai o texto, usa a API da OpenAI para estruturar medicações em JSON e gera uma tabela simples por período do dia.

## Como executar

1. Preencha `OPENAI_API_KEY` no arquivo `.env`.
2. Execute `run_app.bat`.

Se precisar recriar o ambiente:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Segurança

O app não é sistema de prescrição, prontuário ou apoio à decisão clínica. Quando a receita não deixa o horário claro, o item deve ser marcado como `revisar manualmente`.
