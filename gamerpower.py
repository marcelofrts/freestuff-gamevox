"""
Módulo responsável por consultar a API do GamerPower para obter jogos gratuitos ativos
e validar disponibilidade real na loja brasileira da Epic Games e Steam.
"""

import json
import time
import re
from typing import List, Dict, Any, Optional
import config

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    import urllib.request
    HAS_REQUESTS = False

API_BASE_URL = "https://www.gamerpower.com/api"

# Termos que indicam bloqueio regional incompatível com o Brasil
BLOCKED_REGIONS = [
    "us only", "usa only", "north america only", "na only",
    "europe only", "eu only", "asia only", "japan only",
    "not available in brazil", "except brazil", "indisponível no brasil",
    "bloqueado no brasil"
]

_epic_br_cache: Optional[List[Dict[str, Any]]] = None
_epic_br_cache_time: float = 0

def get_epic_games_brazil_free_catalog() -> List[Dict[str, Any]]:
    """Consulta a API oficial da Epic Games Store filtrada para a região do Brasil."""
    global _epic_br_cache, _epic_br_cache_time
    now = time.time()
    # Cache por 10 minutos para não sobrecarregar
    if _epic_br_cache is not None and (now - _epic_br_cache_time) < 600:
        return _epic_br_cache

    url = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=pt-BR&country=BR"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        if HAS_REQUESTS:
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                data = res.json()
                elements = data.get("data", {}).get("Catalog", {}).get("searchStore", {}).get("elements", [])
                _epic_br_cache = elements
                _epic_br_cache_time = now
                return elements
        else:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as r:
                data = json.loads(r.read().decode("utf-8"))
                elements = data.get("data", {}).get("Catalog", {}).get("searchStore", {}).get("elements", [])
                _epic_br_cache = elements
                _epic_br_cache_time = now
                return elements
    except Exception as e:
        print(f"[Aviso] Falha ao consultar catálogo da Epic Games Brasil: {e}")
    return []

def is_epic_game_available_in_brazil(title: str) -> bool:
    """Verifica se o jogo da Epic Games está realmente listado e gratuito na loja brasileira."""
    catalog = get_epic_games_brazil_free_catalog()
    if not catalog:
        # Se a API da Epic falhar, não bloqueia por segurança
        return True
    
    norm_target = re.sub(r"[^a-z0-9]", "", title.lower())
    for el in catalog:
        t = el.get("title", "")
        norm_t = re.sub(r"[^a-z0-9]", "", t.lower())
        price = el.get("price", {}).get("totalPrice", {}).get("discountPrice", 1)
        # Se o título bate e o jogo é 100% grátis no Brasil
        if norm_t in norm_target or norm_target in norm_t:
            if price == 0:
                return True
    return False

def is_giveaway_eligible(giveaway: Dict[str, Any]) -> bool:
    """
    Verifica se o jogo atende a todos os critérios:
    1. Apenas jogos completos (ignora skins/DLCs soltas se TYPE_FILTER for 'game').
    2. Apenas das lojas configuradas (Steam, Epic Games Store, GOG).
    3. Disponível no Brasil (sem restrições regionais).
    """
    platforms = giveaway.get("platforms", "").lower()
    title = giveaway.get("title", "").lower()
    desc = giveaway.get("description", "").lower()
    inst = giveaway.get("instructions", "").lower()
    g_type = giveaway.get("type", "").lower()

    # 1. Filtro de tipo
    if config.TYPE_FILTER != "all" and g_type != config.TYPE_FILTER:
        return False

    # 2. Filtro de lojas permitidas (Steam, Epic Games, GOG)
    if config.ALLOWED_STORES:
        has_allowed_store = any(
            store in platforms or store in title for store in config.ALLOWED_STORES
        )
        if not has_allowed_store:
            return False

    # 3. Filtro de bloqueio regional
    if config.ONLY_BRAZIL:
        full_text = f"{title} {desc} {inst}"
        if any(region in full_text for region in BLOCKED_REGIONS):
            return False

        # Validação direta contra o catálogo oficial da Epic Games Store Brasil
        if "epic" in platforms or "epic" in title:
            if not is_epic_game_available_in_brazil(giveaway.get("title", "")):
                return False

    return True

def fetch_giveaways(platform: str = "pc", giveaway_type: str = "game") -> List[Dict[str, Any]]:
    """Busca jogos gratuitos ativos na GamerPower API."""
    params = []
    if platform and platform != "all":
        params.append(f"platform={platform}")
    if giveaway_type and giveaway_type != "all":
        params.append(f"type={giveaway_type}")
    
    query_string = f"?{'&'.join(params)}" if params else ""
    url = f"{API_BASE_URL}/giveaways{query_string}"
    
    headers = {
        "User-Agent": "FreeStuff-GameVox-Bot/1.0 (+https://gamevox.com)"
    }
    
    try:
        if HAS_REQUESTS:
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    return data
                return []
            else:
                print(f"[Aviso] API GamerPower retornou status {response.status_code}")
                return []
        else:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as res:
                if res.status == 200:
                    raw = res.read().decode("utf-8")
                    data = json.loads(raw)
                    if isinstance(data, list):
                        return data
                    return []
    except Exception as e:
        print(f"[Erro] Falha ao consultar API da GamerPower: {e}")
        return []
