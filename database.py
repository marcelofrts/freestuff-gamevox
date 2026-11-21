"""
Gerenciador de histórico de jogos notificados em arquivo JSON.
O formato JSON é ideal para servidores, Docker e GitHub Actions,
pois é legível por texto e persiste facilmente no controle de versão.
"""

import json
from pathlib import Path
from typing import Dict, Any, List

DATA_DIR = Path(__file__).resolve().parent / "data"
HISTORY_FILE = DATA_DIR / "notified.json"

def _load_history() -> Dict[str, Any]:
    if not HISTORY_FILE.exists():
        return {"notified_ids": [], "games": []}
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict) and "notified_ids" in data:
                return data
            return {"notified_ids": [], "games": []}
    except Exception:
        return {"notified_ids": [], "games": []}

def _save_history(data: Dict[str, Any]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def init_db() -> None:
    """Garante que a pasta e o arquivo de histórico existam."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not HISTORY_FILE.exists():
        _save_history({"notified_ids": [], "games": []})

def is_giveaway_notified(giveaway_id: int) -> bool:
    """Verifica se um jogo com esse ID já foi notificado anteriormente."""
    history = _load_history()
    return giveaway_id in history.get("notified_ids", [])

def record_giveaway(giveaway: dict) -> None:
    """Registra um jogo no histórico JSON."""
    history = _load_history()
    gid = giveaway.get("id")
    if gid and gid not in history["notified_ids"]:
        history["notified_ids"].append(gid)
        history["games"].append({
            "id": gid,
            "title": giveaway.get("title", "Sem título"),
            "worth": giveaway.get("worth", "N/A"),
            "platforms": giveaway.get("platforms", "PC")
        })
        _save_history(history)

def get_total_notified() -> int:
    """Retorna o total de jogos já notificados."""
    history = _load_history()
    return len(history.get("notified_ids", []))

def clear_history() -> None:
    """Limpa o histórico de notificações."""
    _save_history({"notified_ids": [], "games": []})
