"""
Script principal do FreeStuff GameVox.
Monitora jogos grátis e envia alertas automáticos para o canal do GameVox.
"""

import sys
import time
import argparse
from datetime import datetime

import config
import database
import gamerpower
import webhook

def log(message: str) -> None:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {message}", flush=True)

def run_check() -> int:
    """Executa uma verificação de jogos gratuitos e envia os novos."""
    if not config.GAMEVOX_WEBHOOK_URL:
        log("❌ ERRO: GAMEVOX_WEBHOOK_URL não foi preenchida no arquivo .env!")
        log("👉 Abra o arquivo .env, cole a URL do seu webhook e tente novamente.")
        return 0

    log(f"🔍 Consultando novos brindes na GamerPower API...")
    giveaways = gamerpower.fetch_giveaways(
        platform=config.PLATFORM_FILTER,
        giveaway_type=config.TYPE_FILTER
    )

    if not giveaways:
        log("ℹ️ Nenhum brinde ativo encontrado na API no momento.")
        return 0

    # Aplica os filtros refinados: apenas Steam, Epic Games, GOG e liberados no Brasil
    eligible = [g for g in giveaways if gamerpower.is_giveaway_eligible(g)]
    log(f"📦 Total de itens na API: {len(giveaways)} | 🎮 Elegíveis (Steam/Epic/GOG no Brasil): {len(eligible)}")

    if not eligible:
        log("ℹ️ Nenhum jogo das lojas permitidas (Steam, Epic, GOG) elegível no momento.")
        return 0

    new_count = 0
    # Processa os brindes na ordem do mais antigo para o mais novo
    for item in reversed(eligible):
        giveaway_id = item.get("id")
        title = item.get("title", "Sem título")

        if not giveaway_id:
            continue

        if database.is_giveaway_notified(giveaway_id):
            continue

        log(f"🆕 Novo jogo encontrado: {title} (ID #{giveaway_id})")
        success, response_msg = webhook.send_giveaway_webhook(
            webhook_url=config.GAMEVOX_WEBHOOK_URL,
            giveaway=item,
            role_mention=config.NOTIFY_ROLE
        )

        if success:
            database.record_giveaway(item)
            log(f"✅ Enviado com sucesso para o GameVox: {title}")
            new_count += 1
            # Pausa de 2 segundos para respeitar limites de taxa do webhook
            time.sleep(2)
        else:
            log(f"⚠️ Falha ao enviar '{title}': {response_msg}")

    if new_count == 0:
        log("✨ Nenhum novo jogo para notificar (todos já foram enviados anteriormente).")
    else:
        log(f"🎉 Ciclo concluído! {new_count} novo(s) jogo(s) notificado(s).")

    return new_count

def main():
    parser = argparse.ArgumentParser(description="FreeStuff GameVox - Bot de Jogos Grátis")
    parser.add_argument("--test", action="store_true", help="Envia uma mensagem de teste para o Webhook")
    parser.add_argument("--once", action="store_true", help="Executa a verificação apenas uma vez e encerra")
    parser.add_argument("--reset", action="store_true", help="Limpa o histórico de jogos enviados no banco local")
    args = parser.parse_args()

    database.init_db()

    if args.reset:
        database.clear_history()
        log("🗑️ Histórico de notificações locais foi resetado com sucesso.")
        return

    if args.test:
        if not config.GAMEVOX_WEBHOOK_URL:
            log("❌ ERRO: Configure a GAMEVOX_WEBHOOK_URL no arquivo .env antes de testar.")
            return
        log("🚀 Enviando mensagem de teste para o Webhook do GameVox...")
        success, msg = webhook.send_test_message(config.GAMEVOX_WEBHOOK_URL)
        if success:
            log("✅ Sucesso! Mensagem de teste enviada. Verifique o seu canal no GameVox.")
        else:
            log(f"❌ Erro ao enviar teste: {msg}")
        return

    if args.once:
        run_check()
        return

    # Modo contínuo (loop infinito)
    interval_seconds = config.CHECK_INTERVAL_MINUTES * 60
    stores_str = ", ".join(config.ALLOWED_STORES).upper()
    log("==================================================")
    log("  🎮 FreeStuff GameVox Bot iniciado!")
    log(f"  ⏱️ Intervalo de checagem: a cada {config.CHECK_INTERVAL_MINUTES} minutos")
    log(f"  🏬 Lojas permitidas: {stores_str}")
    log(f"  🇧🇷 Apenas jogos disponíveis no Brasil: {'SIM' if config.ONLY_BRAZIL else 'NÃO'}")
    log(f"  📊 Jogos no histórico: {database.get_total_notified()}")
    log("  Pressione CTRL+C para encerrar o bot a qualquer momento.")
    log("==================================================")

    while True:
        try:
            run_check()
            log(f"💤 Aguardando {config.CHECK_INTERVAL_MINUTES} minutos até a próxima verificação...")
            time.sleep(interval_seconds)
        except KeyboardInterrupt:
            log("🛑 Bot encerrado pelo usuário.")
            break
        except Exception as e:
            log(f"⚠️ Ocorreu um erro inesperado no ciclo: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
