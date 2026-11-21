"""
Módulo responsável por consultar a API do GamerPower para obter jogos gratuitos ativos.
"""

import json
from typing import List, Dict, Any, Optional

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    import urllib.request
    HAS_REQUESTS = False

API_BASE_URL = "https://www.gamerpower.com/api"

def fetch_giveaways(platform: str = "pc", giveaway_type: str = "game") -> List[Dict[str, Any]]:
    """
    Busca jogos gratuitos ativos na GamerPower API.
    
    :param platform: 'pc', 'steam', 'epic-games-store', 'gog', 'all', etc.
    :param giveaway_type: 'game', 'loot', 'beta', ou 'all'
    :return: Lista de dicionários contendo os dados dos brindes/jogos.
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
                # A API retorna status 0 caso não haja resultados
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

def get_giveaway_by_id(giveaway_id: int) -> Optional[Dict[str, Any]]:
    """Obtém detalhes de um giveaway específico pelo ID."""
    url = f"{API_BASE_URL}/giveaway?id={giveaway_id}"
    headers = {"User-Agent": "FreeStuff-GameVox-Bot/1.0"}
    try:
        if HAS_REQUESTS:
            res = requests.get(url, headers=headers, timeout=15)
            return res.json() if res.status_code == 200 else None
        else:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as res:
                return json.loads(res.read().decode("utf-8")) if res.status == 200 else None
    except Exception as e:
        print(f"[Erro] Falha ao buscar detalhes do giveaway #{giveaway_id}: {e}")
        return None
