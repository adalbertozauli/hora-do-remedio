# Hora do Remédio

Aplicativo desktop para Windows voltado à organização visual de rotinas medicamentosas a partir de receitas em `.docx`.

O app extrai o texto da receita, usa a API da OpenAI para estruturar os dados em JSON e monta uma tabela editável com os períodos `Cedo`, `Tarde` e `Noite`. A versão final pode ser exportada em PDF.

## O que o app faz

- Importa receitas médicas em `.docx`.
- Extrai o texto do documento.
- Identifica medicamento, dose, posologia, horários e observações.
- Organiza a rotina por período do dia.
- Permite revisão manual em uma tabela editável.
- Exporta PDF em A4 paisagem.
- Inclui nome do paciente, PSF e imagens nos períodos do PDF.
- Permite configurar a chave da OpenAI pelo próprio aplicativo.

## Segurança

Este app é apenas um organizador visual de medicações.

Ele não é:

- sistema de prescrição;
- prontuário eletrônico;
- suporte à decisão clínica;
- software hospitalar.

Regras importantes:

- O app não deve inventar horários.
- Quando houver ambiguidade, deve marcar para revisão manual.
- Se a receita disser apenas `1x ao dia` ou equivalente, o horário fica em branco e a observação recebe `Qualquer horário`.
- Termos como `antes do almoço`, `após o almoço`, `antes do jantar`, `após o jantar` são preservados em `Observações`.

## Instalação para usuário final

Baixe o instalador na página de Releases do GitHub:

```text
HoraDoRemedioSetup-v0.2.0.exe
```

Depois:

1. Execute o instalador.
2. Abra o aplicativo pelo atalho da Área de Trabalho ou Menu Iniciar.
3. Clique em `Configurar chave da API`.
4. Cole sua chave da OpenAI.
5. Importe uma receita `.docx`.

A chave fica salva localmente em:

```text
%APPDATA%\HoraDoRemedio\.env
```

## Desenvolvimento local

Crie o ambiente:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Execute:

```powershell
.\run_app.bat
```

Opcionalmente, configure `.env` na raiz do projeto:

```env
OPENAI_API_KEY=sua_chave_aqui
OPENAI_MODEL=gpt-4o-mini
```

## Gerar executável

Instale o PyInstaller:

```powershell
.\.venv\Scripts\python.exe -m pip install pyinstaller
```

Gere o executável principal:

```powershell
.\.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean --onefile --windowed --name HoraDoRemedio --add-data "assets;assets" .\main.py
```

Gere o instalador:

```powershell
.\.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean --onefile --windowed --name HoraDoRemedioSetup --add-data "dist\HoraDoRemedio.exe;." .\installer\hora_do_remedio_installer.py
```

O instalador final ficará em:

```text
dist\HoraDoRemedioSetup.exe
```

## Tecnologias

- Python
- PySide6
- python-docx
- OpenAI API
- reportlab
- python-dotenv
- PyInstaller
