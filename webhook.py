"""
Módulo para envio de mensagens ricas (Embeds) para o Webhook do GameVox.
Como o GameVox possui compatibilidade com a API do Discord, a estrutura do Embed é idêntica.
"""

import json
from typing import Dict, Any, Tuple

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    import urllib.request
    HAS_REQUESTS = False

def detect_store_color(platforms: str, title: str) -> int:
    """Define a cor lateral do Embed de acordo com a loja/plataforma."""
    text = f"{platforms} {title}".lower()
    if "epic" in text:
        return 0x0078F2  # Azul Epic
    elif "steam" in text:
        return 0x1B2838  # Azul marinho Steam
    elif "gog" in text:
        return 0x862295  # Roxo GOG
    elif "prime" in text or "amazon" in text:
        return 0x00A8E1  # Azul claro Prime
    elif "ubisoft" in text:
        return 0x0070FF  # Azul Ubisoft
    return 0x10B981      # Verde Esmeralda (Padrão 100% OFF)

def build_embed(giveaway: Dict[str, Any]) -> Dict[str, Any]:
    """Cria a estrutura de Embed compatível com GameVox/Discord."""
    title = giveaway.get("title", "Jogo Grátis")
    worth = giveaway.get("worth", "N/A")
    platforms = giveaway.get("platforms", "PC")
    end_date = giveaway.get("end_date", "N/D")
    claim_url = giveaway.get("open_giveaway_url") or giveaway.get("gamerpower_url", "")
    description = giveaway.get("description", "")
    
    # Se a descrição for muito longa, resume
    if len(description) > 300:
        description = description[:297] + "..."

    # Formata data de expiração se disponível
    validade_str = "Por tempo limitado"
    if end_date and end_date.lower() != "n/d":
        validade_str = end_date

    # Preço original riscado
    preco_formatado = f"~~{worth}~~ **100% GRÁTIS**" if worth and worth != "N/A" else "**100% GRÁTIS**"

    color = detect_store_color(platforms, title)

    embed = {
        "title": f"🎁 [GRÁTIS] {title}",
        "url": claim_url,
        "description": f"{description}\n\n👉 **[Clique aqui para resgatar o jogo]({claim_url})**",
        "color": color,
        "fields": [
            {
                "name": "💰 Valor Original",
                "value": preco_formatado,
                "inline": True
            },
            {
                "name": "🕹️ Plataforma",
                "value": platforms,
                "inline": True
            },
            {
                "name": "⏳ Disponibilidade",
                "value": validade_str,
                "inline": True
            }
        ],
        "footer": {
            "text": "FreeStuff GameVox • Notificação Automática",
            "icon_url": "https://img.icons8.com/color/48/controller.png"
        }
    }

    # Imagem de destaque (banner do jogo)
    image_url = giveaway.get("image") or giveaway.get("thumbnail")
    if image_url:
        embed["image"] = {"url": image_url}

    return embed

def send_giveaway_webhook(webhook_url: str, giveaway: Dict[str, Any], role_mention: str = "") -> Tuple[bool, str]:
    """
    Envia a notificação do jogo gratuito para o Webhook do GameVox.
    """
    if not webhook_url:
        return False, "URL do Webhook não configurada no arquivo .env."

    embed = build_embed(giveaway)
    
    payload = {
        "username": "FreeStuff GameVox",
        "avatar_url": "https://img.icons8.com/fluency/96/gift.png",
        "embeds": [embed]
    }

    if role_mention:
        payload["content"] = f"{role_mention} Novo jogo gratuito disponível!"

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "FreeStuff-GameVox-Bot/1.0"
    }

    try:
        data_json = json.dumps(payload).encode("utf-8")
        if HAS_REQUESTS:
            response = requests.post(webhook_url, json=payload, headers=headers, timeout=15)
            # 200, 204 No Content são respostas de sucesso no GameVox/Discord
            if response.status_code in [200, 204]:
                return True, "Enviado com sucesso!"
            else:
                return False, f"Servidor retornou status {response.status_code}: {response.text}"
        else:
            req = urllib.request.Request(webhook_url, data=data_json, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=15) as res:
                if res.status in [200, 204]:
                    return True, "Enviado com sucesso!"
                return False, f"Servidor retornou status {res.status}"
    except Exception as e:
        return False, f"Erro na requisição: {e}"

def send_test_message(webhook_url: str) -> Tuple[bool, str]:
    """Envia uma mensagem de teste simples para confirmar que o Webhook está ativo."""
    test_giveaway = {
        "id": 999999,
        "title": "Jogo de Teste (Exemplo de Notificação)",
        "worth": "$29.99",
        "platforms": "PC, Steam, Epic Games",
        "end_date": "Indeterminado",
        "description": "Se você está vendo esta mensagem no GameVox, seu Webhook está configurado e funcionando perfeitamente!",
        "open_giveaway_url": "https://gamevox.com",
        "image": "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=800&auto=format&fit=crop&q=80"
    }
    return send_giveaway_webhook(webhook_url, test_giveaway)
