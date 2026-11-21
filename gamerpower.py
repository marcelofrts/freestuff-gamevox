"""
Módulo responsável por consultar a API do GamerPower para obter jogos gratuitos ativos.
"""

import json
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

def is_giveaway_eligible(giveaway: Dict[str, Any]) -> bool:
    """
    Verifica se o jogo atende a todos os critérios:
    1. Apenas jogos completos (ignora skins/DLCs soltas se TYPE_FILTER for 'game').
    2. Apenas das lojas configuradas (Steam, Epic Games Store, GOG).
    3. Disponível no Brasil (sem restrições regionais para US/EU apenas).
    """
    platforms = giveaway.get("platforms", "").lower()
    title = giveaway.get("title", "").lower()
    desc = giveaway.get("description", "").lower()
    inst = giveaway.get("instructions", "").lower()
    g_type = giveaway.get("type", "").lower()

    # 1. Filtro de tipo (ignora skins/loot/itens in-game)
    if config.TYPE_FILTER != "all" and g_type != config.TYPE_FILTER:
        return False

    # 2. Filtro de lojas permitidas (Steam, Epic Games, GOG)
    if config.ALLOWED_STORES:
        has_allowed_store = any(
            store in platforms or store in title for store in config.ALLOWED_STORES
        )
        if not has_allowed_store:
            return False

    # 3. Filtro de bloqueio regional (apenas o que pode ser baixado no Brasil)
    if config.ONLY_BRAZIL:
        full_text = f"{title} {desc} {inst}"
        if any(region in full_text for region in BLOCKED_REGIONS):
            return False

    return True

def fetch_giveaways(platform: str = "pc", giveaway_type: str = "game") -> List[Dict[str, Any]]:
    """
    Busca jogos gratuitos ativos na GamerPower API.
    """
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
