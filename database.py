"""
Gerenciador de histórico de jogos notificados em arquivo JSON.
Armazena o período de gratuidade (published_date e end_date) para permitir
que jogos que voltem a ficar gratuitos no futuro sejam novamente notificados.
"""

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional

DATA_DIR = Path(__file__).resolve().parent / "data"
HISTORY_FILE = DATA_DIR / "notified.json"

def _normalize_title(title: str) -> str:
    """Normaliza o título do jogo removendo sufixos como (Epic Games), Giveaway, etc."""
    t = title.lower()
    t = re.sub(r"\(.*?\)", "", t)
    t = t.replace("giveaway", "").replace("free", "").strip()
    return re.sub(r"\s+", " ", t)

def _parse_date(date_str: Optional[str]) -> Optional[datetime]:
    """Converte string de data para datetime UTC."""
    if not date_str or str(date_str).strip().upper() in ("N/A", "N/D", "NONE"):
        return None
    try:
        return datetime.strptime(str(date_str).strip(), "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    except Exception:
        try:
            return datetime.fromisoformat(str(date_str).strip()).replace(tzinfo=timezone.utc)
        except Exception:
            return None

def _load_history() -> Dict[str, Any]:
    if not HISTORY_FILE.exists():
        return {"games": {}}
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Compatibilidade caso o arquivo ainda esteja no formato antigo
            if "games" in data and isinstance(data["games"], dict):
                return data
            elif "notified_ids" in data:
                # Migra lista antiga para o formato novo de dicionário
                migrated = {"games": {}}
                for old_game in data.get("games", []):
                    gid = str(old_game.get("id"))
                    migrated["games"][gid] = old_game
                return migrated
            return {"games": {}}
    except Exception:
        return {"games": {}}

def _save_history(data: Dict[str, Any]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def init_db() -> None:
    """Garante que a pasta e o arquivo de histórico existam."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not HISTORY_FILE.exists():
        _save_history({"games": {}})

def should_notify(giveaway: Dict[str, Any]) -> bool:
    """
    Determina se um jogo deve ser notificado:
    1. Se nunca foi notificado antes ➔ Retorna True.
    2. Se já foi notificado anteriormente:
       - Se a data de término (end_date) ou início (published_date) for mais recente
         do que a registrada anteriormente (ou seja, uma nova promoção do mesmo jogo) ➔ Retorna True.
       - Se for exatamente a mesma promoção que ainda está ativa ➔ Retorna False.
    """
    gid = str(giveaway.get("id"))
    title = giveaway.get("title", "")
    norm_title = _normalize_title(title)
    
    curr_pub = _parse_date(giveaway.get("published_date"))
    curr_end = _parse_date(giveaway.get("end_date"))

    history = _load_history()
    games = history.get("games", {})

    # Procura registro prévio pelo ID ou pelo título normalizado
    record = games.get(gid)
    if not record and norm_title:
        for existing in games.values():
            if existing.get("normalized_title") == norm_title:
                record = existing
                break

    # Se nunca foi notificado antes, é elegível!
    if not record:
        return True

    # Se já foi notificado, verifica se é uma nova rodada de gratuidade
    prev_pub = _parse_date(record.get("published_date"))
    prev_end = _parse_date(record.get("end_date"))

    # Caso 1: Mesma data de término exata -> mesma promoção ainda em andamento
    if curr_end and prev_end and curr_end == prev_end:
        return False

    # Caso 2: Mesma data de publicação -> mesma promoção
    if curr_pub and prev_pub and curr_pub == prev_pub:
        return False

    # Caso 3: A nova data de publicação é mais recente que a data anterior
    if curr_pub and prev_pub and curr_pub > prev_pub:
        return True

    # Caso 4: A nova data de término é mais recente que a anterior
    if curr_end and prev_end and curr_end > prev_end:
        return True

    # Se não há datas na API para comparar, não repete
    return False

def is_giveaway_notified(giveaway_id: int) -> bool:
    """Método legado mantido para retrocompatibilidade."""
    history = _load_history()
    return str(giveaway_id) in history.get("games", {})

def record_giveaway(giveaway: Dict[str, Any]) -> None:
    """
    Registra ou atualiza um jogo no histórico JSON com suas datas de gratuidade.
    """
    gid = str(giveaway.get("id"))
    history = _load_history()
    games = history.setdefault("games", {})

    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    title = giveaway.get("title", "Sem título")

    games[gid] = {
        "id": giveaway.get("id"),
        "title": title,
        "normalized_title": _normalize_title(title),
        "worth": giveaway.get("worth", "N/A"),
        "platforms": giveaway.get("platforms", "PC"),
        "published_date": giveaway.get("published_date"),
        "end_date": giveaway.get("end_date"),
        "last_notified_at": now_str
    }

    _save_history(history)

def get_total_notified() -> int:
    """Retorna o total de jogos únicos salvos no histórico."""
    history = _load_history()
    return len(history.get("games", {}))

def clear_history() -> None:
    """Limpa o histórico de notificações."""
    _save_history({"games": {}})
