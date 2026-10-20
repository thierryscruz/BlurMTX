"""
=============================================================================
BlurMTX — Discord Webhook Broadcaster
=============================================================================
Posta automaticamente no canal do Discord ao final de cada corrida:
- Pódio (1º, 2º e 3º colocados)
- Destaques de combate (MVP, Maior Demolidor, Muralha)
- Resumo de tiros e acertos estilo AMX Mod X
- Tabela do campeonato atualizada
Utiliza urllib.request nativo (zero dependências externas).
=============================================================================
"""

import json
import urllib.request
import urllib.error
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "blur_mtx.json"


def send_discord_match_summary(match_info, standings=None):
    """Envia o resumo da corrida para o canal do Discord via Webhook."""
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    except Exception:
        cfg = {}

    disc_cfg = cfg.get("discord", {})
    if not disc_cfg.get("webhook_enabled", False):
        return False, "Webhook desativado nas configurações."

    webhook_url = disc_cfg.get("webhook_url", "").strip()
    if not webhook_url or not webhook_url.startswith("http"):
        return False, "URL do Webhook do Discord inválida ou vazia."

    track_name = match_info.get("track_name", "Circuito Blur")
    laps = match_info.get("laps", 3)
    winner = match_info.get("winner", "Campeão")
    mvp = match_info.get("mvp", "Nenhum")
    aggressive = match_info.get("most_aggressive", "Nenhum")

    # Monta os campos de destaque
    fields = [
        {"name": "🏁 Circuito", "value": f"**{track_name}** ({laps} voltas)", "inline": True},
        {"name": "🥇 Vencedor", "value": f"🏆 **{winner}**", "inline": True},
        {"name": "⭐ MVP da Corrida", "value": f"🎖️ **{mvp}**", "inline": True},
    ]

    if aggressive and aggressive != "Nenhum":
        fields.append({"name": "💥 Maior Demolidor", "value": f"🎯 **{aggressive}**", "inline": True})

    # Adiciona Top 5 do campeonato se fornecido
    if standings:
        standings_text = ""
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
        for idx, p in enumerate(standings[:5]):
            med = medals[idx] if idx < len(medals) else "▫️"
            standings_text += f"{med} **{p['name']}** — {p['points']} pts ({p['wins']} vitórias)\n"
        
        if standings_text:
            fields.append({"name": "🏆 Classificação do Campeonato (Top 5)", "value": standings_text, "inline": False})

    # Payload oficial do Discord Embed
    payload = {
        "username": "BlurMTX Server",
        "avatar_url": "https://raw.githubusercontent.com/OpenBlur/assets/main/icon.png",
        "embeds": [{
            "title": "⚡ Resultado da Partida — BlurMTX Dedicated Server",
            "description": f"Corrida finalizada com sucesso! Confira os destaques da corrida e a classificação atualizada:",
            "color": 0x00D2FF,  # Ciano Neon
            "fields": fields,
            "footer": {
                "text": "BlurMTX Dedicated Match Analytics • Estilo AMX Mod X"
            }
        }]
    }

    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            webhook_url,
            data=data,
            headers={"Content-Type": "application/json", "User-Agent": "BlurMTX-Bot/1.2"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            return True, f"Enviado com sucesso! HTTP {response.status}"
    except urllib.error.HTTPError as e:
        return False, f"Erro HTTP {e.code}: {e.reason}"
    except Exception as e:
        return False, f"Falha na conexão: {str(e)}"


if __name__ == "__main__":
    test_match = {
        "track_name": "Barcelona — Gràcia",
        "laps": 3,
        "winner": "Thierry",
        "mvp": "Thierry",
        "most_aggressive": "Piloto_2"
    }
    ok, msg = send_discord_match_summary(test_match)
    print(f"Status do teste Discord: {msg}")
