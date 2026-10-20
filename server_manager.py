"""
=============================================================================
BlurMTX — Dedicated Server Orchestrator & Live Watcher
=============================================================================
Orquestrador central do servidor dedicado do Blur:
1. Monitora o término de partidas em tempo real (telemetry_last_match.json).
2. Ingere dados de combate no banco de dados SQLite (blur_mtx.db).
3. Dispara postagens automáticas no Discord Webhook (Pódio + MVP + Standings).
4. Fornece telemetria contínua ao Web Dashboard.
=============================================================================
"""

import sys
import os
import time
import json
from pathlib import Path

# Garante suporte a UTF-8 no console Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from analytics.database import init_database, process_match_telemetry, get_leaderboard
from analytics.discord_bot import send_discord_match_summary

TELEMETRY_PATH = BASE_DIR / "telemetry_last_match.json"
CONFIG_PATH = BASE_DIR / "blur_mtx.json"


def watch_and_orchestrate():
    init_database()
    print("=====================================================================")
    print("  ⚡ BlurMTX — Orquestrador do Servidor Dedicado Iniciado")
    print("=====================================================================")
    print("  ✓ Banco de Dados SQLite: blur_mtx.db (Ativo)")
    print("  ✓ Monitorando telemetria de corridas e partidas...")
    print("  Pressione Ctrl+C para encerrar.")
    print("=====================================================================\n")

    last_mtime = 0
    if TELEMETRY_PATH.exists():
        last_mtime = TELEMETRY_PATH.stat().st_mtime

    while True:
        try:
            if TELEMETRY_PATH.exists():
                cur_mtime = TELEMETRY_PATH.stat().st_mtime
                if cur_mtime > last_mtime:
                    last_mtime = cur_mtime
                    time.sleep(0.5)  # Breve pausa para garantir que o arquivo foi totalmente gravado

                    try:
                        with open(TELEMETRY_PATH, "r", encoding="utf-8") as f:
                            data = json.load(f)
                    except Exception as e:
                        print(f"[BlurMTX] Aguardando gravação completa do log: {e}")
                        continue

                    print("\n" + "=" * 60)
                    print(f"🏁 [BlurMTX] Nova corrida detectada em {data.get('timestamp')}!")
                    
                    # 1. Ingestão no Banco de Dados
                    summary = process_match_telemetry(data)
                    print(f"  🥇 Vencedor: {summary['winner']}")
                    print(f"  ⭐ MVP da Partida: {summary['mvp']}")
                    if summary.get('most_aggressive'):
                        print(f"  💥 Maior Demolidor: {summary['most_aggressive']}")

                    # 2. Notificação no Discord
                    leaderboard = get_leaderboard()
                    ok_disc, msg_disc = send_discord_match_summary({
                        "track_name": data.get("track_name", "Circuito"),
                        "laps": data.get("laps", 3),
                        "winner": summary["winner"],
                        "mvp": summary["mvp"],
                        "most_aggressive": summary.get("most_aggressive")
                    }, standings=leaderboard)

                    if ok_disc:
                        print(f"  📡 Discord: {msg_disc}")

                    print("=" * 60 + "\n")

            time.sleep(2)
        except KeyboardInterrupt:
            print("\n[BlurMTX] Orquestrador encerrado pelo usuário.")
            break
        except Exception as e:
            print(f"[BlurMTX] Erro no loop de orquestração: {e}")
            time.sleep(2)


if __name__ == "__main__":
    watch_and_orchestrate()
