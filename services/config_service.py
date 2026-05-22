import os
import sys
from pathlib import Path

from dotenv import load_dotenv


APP_DIR_NAME = "HoraDoRemedio"


def app_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[1]


def user_config_dir() -> Path:
    root = os.getenv("APPDATA") or str(Path.home())
    return Path(root) / APP_DIR_NAME


def user_env_path() -> Path:
    return user_config_dir() / ".env"


def load_app_environment() -> None:
    load_dotenv()
    load_dotenv(app_base_dir() / ".env", override=False)
    load_dotenv(user_env_path(), override=True)


def save_openai_key(api_key: str, model: str = "gpt-4o-mini") -> Path:
    config_dir = user_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)
    env_path = user_env_path()
    selected_model = model.strip() or "gpt-4o-mini"
    env_path.write_text(
        f"OPENAI_API_KEY={api_key.strip()}\nOPENAI_MODEL={selected_model}\n",
        encoding="utf-8",
    )
    os.environ["OPENAI_API_KEY"] = api_key.strip()
    os.environ["OPENAI_MODEL"] = selected_model
    return env_path
