"""
Configurações do FreeStuff para GameVox
Carrega variáveis de ambiente de um arquivo .env ou do sistema.
"""

import os
from pathlib import Path

# Carregador simples de .env nativo (caso python-dotenv não esteja instalado)
def load_dotenv_fallback(env_path: Path):
    if not env_path.exists():
        return
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip().strip("'\"")
                if key not in os.environ:
                    os.environ[key] = val
    except Exception:
        pass

# Tenta carregar com python-dotenv, ou usa o fallback nativo
ENV_FILE = Path(__file__).resolve().parent / ".env"
try:
    from dotenv import load_dotenv
    load_dotenv(ENV_FILE)
except ImportError:
    load_dotenv_fallback(ENV_FILE)

# Configurações do Bot
GAMEVOX_WEBHOOK_URL = os.getenv("GAMEVOX_WEBHOOK_URL", "").strip()
CHECK_INTERVAL_MINUTES = int(os.getenv("CHECK_INTERVAL_MINUTES", "15"))
PLATFORM_FILTER = os.getenv("PLATFORM_FILTER", "pc").strip().lower()
TYPE_FILTER = os.getenv("TYPE_FILTER", "game").strip().lower()
NOTIFY_ROLE = os.getenv("NOTIFY_ROLE", "").strip()

# Caminho do banco de dados SQLite local
DATA_DIR = Path(__file__).resolve().parent / "data"
DATABASE_PATH = DATA_DIR / "giveaways.db"
