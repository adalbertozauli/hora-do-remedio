# AGENTS.md

## Projeto
Nome: Hora do Remédio

Aplicativo desktop para Windows voltado para organização visual de rotinas medicamentosas para idosos e familiares.

O sistema importa receitas médicas em .docx, extrai o texto, identifica medicamentos e horários de uso, e gera uma tabela simples organizada por períodos do dia:
- cedo
- tarde
- noite

O foco principal é clareza visual, simplicidade e segurança.

---

# Objetivos do projeto

O aplicativo deve:
1. Ler receitas médicas em .docx
2. Extrair texto de forma limpa
3. Utilizar OpenAI API para estruturar os dados
4. Identificar:
   - medicamento
   - dose
   - posologia
   - horários
5. Montar tabela visual editável
6. Exportar PDF legível para idosos

---

# Regras críticas

## Segurança
- Nunca inventar horários.
- Se houver ambiguidade:
  - marcar como "revisar manualmente"
- Não assumir informações ausentes.
- Não inferir indicação clínica.
- Não alterar nomes de medicamentos sem confiança alta.

## Escopo
Este NÃO é:
- sistema de prescrição
- prontuário eletrônico
- suporte à decisão médica
- software hospitalar

Este é apenas:
- organizador visual de medicações

---

# Tecnologias obrigatórias

- Python
- PySide6
- python-docx
- OpenAI API
- reportlab
- python-dotenv

Evitar dependências extras sem necessidade clara.

---

# Estrutura desejada

```text
hora_do_remedio/

├── main.py
├── requirements.txt
├── .env
│
├── ui/
│   ├── main_window.py
│   ├── styles.py
│
├── services/
│   ├── doc_reader.py
│   ├── openai_service.py
│   ├── medication_parser.py
│   ├── pdf_generator.py
│
├── models/
│   ├── medication.py
│
├── utils/
│   ├── horario_mapper.py
│   ├── validators.py
│
├── outputs/
│
└── assets/