"""
=============================================================================
BlurMTX — Live Web Dashboard & Telemetry Server
=============================================================================
Servidor Web com interface ultra-moderna em tempo real:
- Painel Administrativo Completo: Edição de pistas, voltas e regras direto pelo navegador/celular
- Presets de Modos de Jogo em 1 Clique (F1 Grand Prix, Caos Demolition, Clean Racing, BoP, Blur Padrão)
- Exibe e edita TODAS as opções configuradas no servidor (Power-ups, Regras, BoP, Pistas)
- Placar e classificação geral do campeonato (estilo Fórmula 1)
- Matriz de combate em tempo real ("quem atirou em quem" estilo AMX Mod X)
- Zero dependências externas (utiliza http.server nativo do Python).
=============================================================================
"""

import sys
import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse

# Garante suporte a UTF-8 no console Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from analytics.database import get_leaderboard, get_recent_matches, get_all_combat_matrix, get_db

PORT = 8080
CONFIG_PATH = BASE_DIR / "blur_mtx.json"
TRACKS_PATH = BASE_DIR / "tracks.json"
PRESETS_PATH = BASE_DIR / "presets.json"
TELEMETRY_PATH = BASE_DIR / "telemetry_last_match.json"


def load_json_safe(path):
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_config_safe(cfg):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


def get_current_server_status():
    """Lê todas as configurações, metadados, presets e status do banco de dados."""
    cfg = load_json_safe(CONFIG_PATH)
    tracks_meta = load_json_safe(TRACKS_PATH)
    presets = load_json_safe(PRESETS_PATH)
    telemetry = load_json_safe(TELEMETRY_PATH)

    return {
        "server": cfg.get("server", {}),
        "powerup_options": cfg.get("powerup_options", {}),
        "advanced_options": cfg.get("advanced_options", {}),
        "gameplay": cfg.get("gameplay", {}),
        "network": cfg.get("network", {}),
        "rotation_playlist": cfg.get("rotation_playlist", []),
        "tracks_meta": tracks_meta if isinstance(tracks_meta, list) else [],
        "presets": presets,
        "telemetry": telemetry,
        "leaderboard": get_leaderboard(),
        "recent_matches": get_recent_matches(10),
        "combat_matrix": get_all_combat_matrix()
    }


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BlurMTX — Live Server & Match Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #090c12;
            --surface: #121724;
            --surface-hover: #192033;
            --surface-card: #151b2a;
            --border: #242f47;
            --border-highlight: #3b4b70;
            --cyan: #00d2ff;
            --cyan-glow: rgba(0, 210, 255, 0.35);
            --pink: #ff007f;
            --orange: #ff6b00;
            --green: #10b981;
            --text: #f1f5f9;
            --text-muted: #8493ad;
            --pw-nitro: #22c55e;
            --pw-barge: #c084fc;
            --pw-shunt: #ef4444;
            --pw-bolt: #f472b6;
            --pw-repair: #eab308;
            --pw-shield: #38bdf8;
            --pw-mine: #fb923c;
            --pw-shock: #60a5fa;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', sans-serif;
            background: var(--bg);
            color: var(--text);
            padding: 20px;
            padding-bottom: 90px;
            min-height: 100vh;
        }

        /* Top Header */
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: 16px;
            border-bottom: 1px solid var(--border);
            margin-bottom: 20px;
            flex-wrap: wrap;
            gap: 12px;
        }

        .logo {
            font-family: 'Orbitron', sans-serif;
            font-size: 24px;
            font-weight: 900;
            color: var(--cyan);
            letter-spacing: 1px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .badge-live {
            background: rgba(16, 185, 129, 0.15);
            color: var(--green);
            border: 1px solid var(--green);
            font-size: 11px;
            font-weight: 700;
            padding: 4px 10px;
            border-radius: 20px;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.7; transform: scale(0.98); }
        }

        /* Presets Bar */
        .presets-section {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 20px;
        }

        .presets-title {
            font-family: 'Orbitron', sans-serif;
            font-size: 12px;
            font-weight: 700;
            color: var(--cyan);
            letter-spacing: 1px;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .presets-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
        }

        .preset-card {
            background: var(--surface-card);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 12px;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }

        .preset-card:hover {
            border-color: var(--cyan);
            transform: translateY(-2px);
            box-shadow: 0 4px 14px rgba(0, 210, 255, 0.15);
        }

        .preset-name {
            font-family: 'Orbitron', sans-serif;
            font-size: 13px;
            font-weight: 700;
            color: var(--text);
            display: flex;
            align-items: center;
            gap: 6px;
            margin-bottom: 4px;
        }

        .preset-desc {
            font-size: 11px;
            color: var(--text-muted);
            line-height: 1.3;
            margin-bottom: 8px;
        }

        .btn-apply-preset {
            background: transparent;
            border: 1px solid var(--cyan);
            color: var(--cyan);
            font-family: 'Orbitron', sans-serif;
            font-size: 10px;
            font-weight: 700;
            padding: 5px 8px;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.15s;
            align-self: flex-start;
        }

        .btn-apply-preset:hover {
            background: var(--cyan);
            color: #000;
        }

        /* Abas de Navegação */
        .tabs {
            display: flex;
            gap: 8px;
            border-bottom: 1px solid var(--border);
            margin-bottom: 20px;
            overflow-x: auto;
        }

        .tab-btn {
            font-family: 'Orbitron', sans-serif;
            font-size: 12px;
            font-weight: 700;
            padding: 10px 16px;
            background: transparent;
            color: var(--text-muted);
            border: none;
            border-bottom: 2px solid transparent;
            cursor: pointer;
            transition: all 0.2s;
            white-space: nowrap;
        }

        .tab-btn:hover { color: var(--text); }
        .tab-btn.active {
            color: var(--cyan);
            border-bottom: 2px solid var(--cyan);
        }

        .tab-content { display: none; }
        .tab-content.active { display: block; }

        /* Grid e Cards */
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 16px;
            margin-bottom: 20px;
        }

        .card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 18px;
            position: relative;
            overflow: hidden;
        }

        .card::before {
            content: '';
            position: absolute;
            top: 0; left: 0; width: 4px; height: 100%;
            background: var(--cyan);
        }

        .card.pink::before { background: var(--pink); }
        .card.orange::before { background: var(--orange); }
        .card.green::before { background: var(--green); }

        .card-title {
            font-family: 'Orbitron', sans-serif;
            font-size: 13px;
            color: var(--text-muted);
            margin-bottom: 14px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        /* Form Controls */
        .form-group {
            margin-bottom: 14px;
        }

        .form-label {
            font-size: 12px;
            color: var(--text-muted);
            margin-bottom: 6px;
            display: block;
            font-weight: 600;
        }

        .form-control, select, input[type="number"], input[type="text"] {
            background: var(--surface-card);
            border: 1px solid var(--border);
            color: var(--text);
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 13px;
            font-family: 'Inter', sans-serif;
            outline: none;
            transition: border-color 0.2s;
            width: 100%;
        }

        .form-control:focus, select:focus, input:focus {
            border-color: var(--cyan);
        }

        /* Toggle Buttons / Badges */
        .toggle-btn {
            background: var(--surface-card);
            border: 1px solid var(--border);
            color: var(--text-muted);
            padding: 7px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            transition: all 0.2s;
            user-select: none;
        }

        .toggle-btn.active {
            border-color: currentColor;
            background: rgba(255, 255, 255, 0.05);
            font-weight: 700;
        }

        .toggle-btn:not(.active) {
            opacity: 0.45;
            text-decoration: line-through;
        }

        /* Checklist de Pistas */
        .batch-toolbar {
            display: flex;
            gap: 10px;
            align-items: center;
            flex-wrap: wrap;
            background: var(--surface-card);
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 16px;
            border: 1px solid var(--border);
        }

        .btn-action {
            background: var(--surface-hover);
            border: 1px solid var(--border-highlight);
            color: var(--text);
            font-size: 11px;
            font-weight: 600;
            padding: 6px 12px;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.15s;
        }

        .btn-action:hover {
            background: var(--cyan);
            color: #000;
            border-color: var(--cyan);
        }

        .track-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 12px;
        }

        .track-card {
            background: var(--surface-card);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 12px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            transition: all 0.2s;
        }

        .track-card.active {
            border-color: rgba(0, 210, 255, 0.4);
            background: rgba(0, 210, 255, 0.02);
        }

        .track-card.inactive {
            opacity: 0.5;
            border-color: var(--border);
        }

        .track-info {
            display: flex;
            align-items: center;
            gap: 10px;
            flex: 1;
        }

        .track-title {
            font-size: 13px;
            font-weight: 600;
            color: var(--text);
        }

        .track-sub {
            font-size: 11px;
            color: var(--text-muted);
        }

        .track-laps-wrapper {
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .track-laps-input {
            width: 58px;
            text-align: center;
            padding: 4px 6px;
            font-family: 'Orbitron', sans-serif;
            font-weight: 700;
            font-size: 13px;
            color: var(--cyan);
        }

        /* Tabelas */
        .table-responsive {
            width: 100%;
            overflow-x: auto;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            text-align: left;
        }

        th {
            font-family: 'Orbitron', sans-serif;
            font-size: 11px;
            color: var(--text-muted);
            padding: 10px 12px;
            border-bottom: 1px solid var(--border);
            text-transform: uppercase;
        }

        td {
            padding: 11px 12px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            font-size: 13px;
        }

        tr:hover td { background: var(--surface-hover); }

        .rank-1 { color: #f59e0b; font-weight: 900; }
        .rank-2 { color: #94a3b8; font-weight: 700; }
        .rank-3 { color: #b45309; font-weight: 700; }

        .pts-badge {
            background: rgba(0, 210, 255, 0.15);
            color: var(--cyan);
            font-weight: 700;
            font-size: 11px;
            padding: 2px 8px;
            border-radius: 4px;
        }

        /* Floating Sticky Action Bar */
        .save-bar {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: rgba(18, 23, 36, 0.95);
            backdrop-filter: blur(10px);
            border-top: 1px solid var(--cyan);
            padding: 14px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            z-index: 999;
            box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.6);
        }

        .btn-save {
            background: linear-gradient(135deg, var(--cyan), #0099cc);
            color: #000;
            font-family: 'Orbitron', sans-serif;
            font-size: 13px;
            font-weight: 900;
            padding: 12px 24px;
            border-radius: 8px;
            border: none;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 8px;
            box-shadow: 0 0 15px var(--cyan-glow);
            transition: all 0.2s;
        }

        .btn-save:hover {
            transform: scale(1.03);
            box-shadow: 0 0 25px rgba(0, 210, 255, 0.6);
        }

        /* Toast */
        .toast {
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--surface);
            border: 1px solid var(--green);
            color: var(--green);
            padding: 12px 20px;
            border-radius: 8px;
            font-weight: 600;
            font-size: 13px;
            z-index: 1000;
            display: none;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
            animation: slideIn 0.3s forwards;
        }

        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
    </style>
</head>
<body>

    <div id="toast" class="toast"></div>

    <!-- Cabeçalho -->
    <div class="header">
        <div class="logo">
            <span>⚡ BLURMTX</span>
            <span style="font-size: 12px; color: var(--pink); font-weight: 700;">AMX DEDICATED</span>
            <span class="badge-live">● SERVIDOR ATIVO</span>
        </div>
        <div style="font-size: 12px; color: var(--text-muted);" id="last-update">
            Carregando telemetria...
        </div>
    </div>

    <!-- PRESETS DE MODOS DE JOGO (1-CLIQUE) -->
    <div class="presets-section">
        <div class="presets-title">
            <span>⚡ PRESETS RÁPIDOS DE JOGO (1-CLIQUE)</span>
            <span style="font-size: 11px; color: var(--text-muted); font-family: 'Inter', sans-serif;">Clique para preencher e aplicar as regras instantaneamente</span>
        </div>
        <div class="presets-grid" id="presets-container">
            <!-- Renderizado dinamicamente -->
        </div>
    </div>

    <!-- Navegação por Abas -->
    <div class="tabs">
        <button class="tab-btn active" onclick="switchTab('tab-live', event)">🏆 AO VIVO & CAMPEONATO</button>
        <button class="tab-btn" onclick="switchTab('tab-tracks', event)">🏁 ROTAÇÃO DE PISTAS (18 MAPAS)</button>
        <button class="tab-btn" onclick="switchTab('tab-rules', event)">⚡ REGRAS DE POWER-UPS & SALA</button>
        <button class="tab-btn" onclick="switchTab('tab-bop', event)">🏎️ BoP & MULTI-CLASS</button>
        <button class="tab-btn" onclick="switchTab('tab-combat', event)">🎯 MATRIZ DE COMBATE (AMX)</button>
    </div>

    <!-- ABA 1: AO VIVO & CAMPEONATO -->
    <div id="tab-live" class="tab-content active">
        <div class="grid">
            <div class="card">
                <div class="card-title">
                    <span>🏁 CONFIGURAÇÃO DA SALA & LARGADA</span>
                    <span style="color: var(--cyan); font-weight: 700;" id="srv-mode-badge">SEQUENCIAL</span>
                </div>
                <div class="grid" style="grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 0;">
                    <div class="form-group">
                        <label class="form-label">Modo de Largada</label>
                        <select id="cfg-auto-start" class="form-control">
                            <option value="false">Manual (Host aguarda todos conectarem)</option>
                            <option value="true">Automático (Countdown de largada)</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Countdown (segundos)</label>
                        <input type="number" id="cfg-countdown" class="form-control" min="5" max="60" value="20">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Modo da Rotação</label>
                        <select id="cfg-rot-mode" class="form-control">
                            <option value="sequential">Sequencial (Ordem da lista)</option>
                            <option value="random">Aleatório (Sorteio)</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Voltas Padrão (Fallback)</label>
                        <input type="number" id="cfg-def-laps" class="form-control" min="1" max="99" value="3">
                    </div>
                </div>
            </div>

            <div class="card pink">
                <div class="card-title">
                    <span>🎯 DESTAQUES DA ÚLTIMA CORRIDA</span>
                    <span style="color: var(--pink); font-weight: 700;">AMX MOD X</span>
                </div>
                <div id="combat-feed">
                    <div style="padding: 10px 0; color: var(--text-muted);">Aguardando encerramento da corrida...</div>
                </div>
            </div>
        </div>

        <div class="card" style="margin-bottom: 24px;">
            <div class="card-title">
                <span>🏆 CLASSIFICAÇÃO GERAL DO CAMPEONATO (FÓRMULA 1)</span>
                <span style="color: var(--cyan); font-size: 12px;">Top Pilotos</span>
            </div>
            <div class="table-responsive">
                <table>
                    <thead>
                        <tr>
                            <th>POS</th>
                            <th>PILOTO</th>
                            <th>CORRIDAS</th>
                            <th>VITÓRIAS</th>
                            <th>PÓDIOS</th>
                            <th>ACERTOS</th>
                            <th>WRECKS</th>
                            <th>MVPs</th>
                            <th>PONTOS</th>
                        </tr>
                    </thead>
                    <tbody id="leaderboard-body">
                        <tr><td colspan="9" style="text-align: center; color: var(--text-muted);">Carregando classificação...</td></tr>
                    </tbody>
                </table>
            </div>
        </div>

        <div class="card orange">
            <div class="card-title">
                <span>📜 HISTÓRICO DE PARTIDAS RECENTES</span>
                <span style="color: var(--orange); font-size: 12px;">Últimas Corridas</span>
            </div>
            <div class="table-responsive">
                <table>
                    <thead>
                        <tr>
                            <th>DATA/HORA</th>
                            <th>PISTA</th>
                            <th>VOLTAS</th>
                            <th>VENCEDOR</th>
                            <th>PILOTOS</th>
                            <th>MVP DA CORRIDA</th>
                        </tr>
                    </thead>
                    <tbody id="matches-body">
                        <tr><td colspan="6" style="text-align: center; color: var(--text-muted);">Nenhuma corrida registrada ainda.</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- ABA 2: ROTAÇÃO DE PISTAS (CHECKLIST DOS 18 MAPAS) -->
    <div id="tab-tracks" class="tab-content">
        <div class="card" style="margin-bottom: 20px;">
            <div class="card-title">
                <span>🏁 PLAYLIST DE ROTAÇÃO DE PISTAS (18 MAPAS OFICIAIS)</span>
                <span style="color: var(--cyan); font-size: 12px;" id="tracks-active-count">0 ativas</span>
            </div>

            <div class="batch-toolbar">
                <button class="btn-action" onclick="setAllTracks(true)">✓ Marcar Todas</button>
                <button class="btn-action" onclick="setAllTracks(false)">✗ Desmarcar Todas</button>
                <div style="display: flex; align-items: center; gap: 6px; margin-left: auto;">
                    <span style="font-size: 11px; color: var(--text-muted);">Aplicar em lote nos circuitos:</span>
                    <input type="number" id="batch-laps" min="1" max="99" value="3" style="width: 50px; text-align: center;" class="form-control">
                    <button class="btn-action" onclick="applyBatchLaps()">Aplicar Voltas</button>
                </div>
            </div>

            <div class="track-grid" id="playlist-container">
                <!-- Renderizado dinamicamente via JS -->
            </div>
        </div>
    </div>

    <!-- ABA 3: REGRAS DE POWER-UPS & OPÇÕES AVANÇADAS -->
    <div id="tab-rules" class="tab-content">
        <div class="grid">
            <div class="card green">
                <div class="card-title">
                    <span>⚡ POWER-UPS (ARMAS)</span>
                    <span style="font-size: 11px; color: var(--text-muted);">Clique para ligar/desligar</span>
                </div>
                
                <div class="form-group">
                    <label class="form-label">Taxa de Respawn dos Power-ups</label>
                    <select id="cfg-pw-respawn" class="form-control">
                        <option value="None">None (Sem armas no chão)</option>
                        <option value="Slow">Slow (Respawn Lento)</option>
                        <option value="Normal">Normal (Padrão do jogo)</option>
                        <option value="Fast">Fast (Respawn Acelerado / Caos)</option>
                    </select>
                </div>

                <div id="powerups-container" style="display: flex; flex-wrap: wrap; gap: 8px; margin-top: 14px;">
                    <!-- Badges interativas -->
                </div>
            </div>

            <div class="card">
                <div class="card-title">
                    <span>⚙️ OPÇÕES AVANÇADAS DA SALA</span>
                    <span style="color: var(--cyan); font-size: 12px;">Oficial Blur</span>
                </div>
                <div class="grid" style="grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 0;">
                    <div class="form-group">
                        <label class="form-label">Dano Veicular (Damage)</label>
                        <select id="cfg-adv-damage" class="form-control">
                            <option value="None">None (Sem danos)</option>
                            <option value="Low">Low (Dano Baixo)</option>
                            <option value="Medium">Medium (Padrão)</option>
                            <option value="High">High (Destruição Rápida)</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Handicap (Auxílio)</label>
                        <select id="cfg-adv-handicap" class="form-control">
                            <option value="None">None (Competitivo Puro)</option>
                            <option value="Low">Low</option>
                            <option value="Medium">Medium</option>
                            <option value="High">High (Recuperação Rápida)</option>
                        </select>
                    </div>
                </div>

                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 10px;">
                    <label style="display: flex; align-items: center; gap: 8px; font-size: 13px; cursor: pointer;">
                        <input type="checkbox" id="cfg-adv-respawn"> Respawn Automático
                    </label>
                    <label style="display: flex; align-items: center; gap: 8px; font-size: 13px; cursor: pointer;">
                        <input type="checkbox" id="cfg-adv-timeout"> Tempo Limite de Chegada
                    </label>
                    <label style="display: flex; align-items: center; gap: 8px; font-size: 13px; cursor: pointer;">
                        <input type="checkbox" id="cfg-adv-mods"> Mods de Carro Liberados
                    </label>
                    <label style="display: flex; align-items: center; gap: 8px; font-size: 13px; cursor: pointer;">
                        <input type="checkbox" id="cfg-adv-upgrades"> Upgrades Liberados
                    </label>
                    <label style="display: flex; align-items: center; gap: 8px; font-size: 13px; cursor: pointer;">
                        <input type="checkbox" id="cfg-adv-ai"> Bots de IA na Sala
                    </label>
                </div>
            </div>
        </div>
    </div>

    <!-- ABA 4: BoP & MULTI-CLASS -->
    <div id="tab-bop" class="tab-content">
        <div class="card orange">
            <div class="card-title">
                <span>🏎️ BALANCE OF PERFORMANCE PROPORCIONAL</span>
                <span style="color: var(--orange); font-weight: 700;">ALVO: VELOCIDADE CLASSE A</span>
            </div>
            <div style="font-size: 13px; color: var(--text-muted); margin-bottom: 16px;">
                Nivela a velocidade máxima e torque de qualquer carro para disputar com o Classe A (~185-195 mph), preservando 100% o peso, aderência e estilo de curva originais.
            </div>

            <div style="margin-bottom: 16px;">
                <label style="display: flex; align-items: center; gap: 8px; font-size: 14px; font-weight: 700; cursor: pointer;">
                    <input type="checkbox" id="cfg-bop-enabled"> Ativar Balance of Performance (BoP)
                </label>
            </div>

            <div class="grid" style="margin-bottom: 0;">
                <div style="background: var(--surface-card); padding: 14px; border-radius: 8px; border: 1px solid var(--border);">
                    <div style="color: var(--orange); font-weight: 700; margin-bottom: 6px;">🚗 CLASSE D (Fusca / Beetle)</div>
                    <input type="number" step="0.01" min="1.0" max="2.0" id="cfg-bop-d" class="form-control" style="font-size: 18px; font-weight: 900; color: var(--orange); text-align: center;">
                    <div style="font-size: 11px; color: var(--text-muted); margin-top: 6px;">Multiplicador (Padrão: 1.48x para 185mph)</div>
                </div>
                <div style="background: var(--surface-card); padding: 14px; border-radius: 8px; border: 1px solid var(--border);">
                    <div style="color: var(--cyan); font-weight: 700; margin-bottom: 6px;">🚙 CLASSE C (Land Rover / Golf)</div>
                    <input type="number" step="0.01" min="1.0" max="1.8" id="cfg-bop-c" class="form-control" style="font-size: 18px; font-weight: 900; color: var(--cyan); text-align: center;">
                    <div style="font-size: 11px; color: var(--text-muted); margin-top: 6px;">Multiplicador (Padrão: 1.28x para 185mph)</div>
                </div>
                <div style="background: var(--surface-card); padding: 14px; border-radius: 8px; border: 1px solid var(--border);">
                    <div style="color: var(--green); font-weight: 700; margin-bottom: 6px;">🏎️ CLASSE B (BMW M3 / 350Z)</div>
                    <input type="number" step="0.01" min="1.0" max="1.5" id="cfg-bop-b" class="form-control" style="font-size: 18px; font-weight: 900; color: var(--green); text-align: center;">
                    <div style="font-size: 11px; color: var(--text-muted); margin-top: 6px;">Multiplicador (Padrão: 1.14x para 185mph)</div>
                </div>
                <div style="background: var(--surface-card); padding: 14px; border-radius: 8px; border: 1px solid var(--border);">
                    <div style="color: var(--text-muted); font-weight: 700; margin-bottom: 6px;">🏁 CLASSE A (Astra / Viper)</div>
                    <div style="font-size: 20px; font-weight: 900; text-align: center; padding: 7px 0; color: var(--text);">1.00x</div>
                    <div style="font-size: 11px; color: var(--text-muted); margin-top: 6px;">Base de referência inalterada</div>
                </div>
            </div>
        </div>
    </div>

    <!-- ABA 5: MATRIZ DE COMBATE -->
    <div id="tab-combat" class="tab-content">
        <div class="card pink">
            <div class="card-title">
                <span>🎯 MATRIZ DE COMBATE ("QUEM ATIROU EM QUEM")</span>
                <span style="color: var(--pink); font-size: 12px;">Top Confrontos</span>
            </div>
            <div class="table-responsive">
                <table>
                    <thead>
                        <tr>
                            <th>ATACANTE</th>
                            <th></th>
                            <th>VÍTIMA</th>
                            <th>ARMA UTILIZADA</th>
                            <th>TOTAL DE ACERTOS</th>
                        </tr>
                    </thead>
                    <tbody id="combat-matrix-body">
                        <tr><td colspan="5" style="text-align: center; color: var(--text-muted);">Nenhum combate registrado ainda.</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- Floating Sticky Action Bar -->
    <div class="save-bar">
        <div style="font-size: 12px; color: var(--text-muted);">
            Alterações não salvas serão aplicadas no servidor após clicar em Salvar.
        </div>
        <button class="btn-save" onclick="saveAllToServer()">
            <span>💾 SALVAR CONFIGURAÇÕES NO SERVIDOR</span>
        </button>
    </div>

    <script>
        let currentConfig = {};
        let tracksMetaMap = {};
        let presetsMap = {};

        const PW_DEFS = [
            { key: 'nitro', name: 'Nitro', col: 'var(--pw-nitro)' },
            { key: 'barge', name: 'Barge', col: 'var(--pw-barge)' },
            { key: 'shunt', name: 'Shunt', col: 'var(--pw-shunt)' },
            { key: 'bolt', name: 'Bolt', col: 'var(--pw-bolt)' },
            { key: 'repair', name: 'Repair', col: 'var(--pw-repair)' },
            { key: 'shield', name: 'Shield', col: 'var(--pw-shield)' },
            { key: 'mine', name: 'Mine', col: 'var(--pw-mine)' },
            { key: 'shock', name: 'Shock', col: 'var(--pw-shock)' },
        ];

        function showToast(msg, isError = false) {
            const toast = document.getElementById('toast');
            toast.innerText = msg;
            toast.style.borderColor = isError ? 'var(--pw-shunt)' : 'var(--green)';
            toast.style.color = isError ? 'var(--pw-shunt)' : 'var(--green)';
            toast.style.display = 'block';
            setTimeout(() => { toast.style.display = 'none'; }, 4000);
        }

        function switchTab(tabId, ev) {
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            
            if (ev) ev.target.classList.add('active');
            document.getElementById(tabId).classList.add('active');
        }

        function togglePowerup(key) {
            if (!currentConfig.powerup_options) currentConfig.powerup_options = {};
            currentConfig.powerup_options[key] = !currentConfig.powerup_options[key];
            renderPowerups();
        }

        function renderPowerups() {
            const pw = currentConfig.powerup_options || {};
            const container = document.getElementById('powerups-container');
            container.innerHTML = PW_DEFS.map(p => {
                const isAct = pw[p.key] !== false;
                return `
                    <div class="toggle-btn ${isAct ? 'active' : ''}" style="color: ${p.col};" onclick="togglePowerup('${p.key}')">
                        <span>●</span>
                        <span>${p.name}</span>
                    </div>
                `;
            }).join('');
        }

        function renderPresets() {
            const container = document.getElementById('presets-container');
            const keys = Object.keys(presetsMap);
            if (keys.length === 0) return;

            container.innerHTML = keys.map(k => {
                const pr = presetsMap[k];
                return `
                    <div class="preset-card">
                        <div>
                            <div class="preset-name">${pr.icon || '⚡'} ${pr.name}</div>
                            <div class="preset-desc">${pr.description}</div>
                        </div>
                        <button class="btn-apply-preset" onclick="applyPreset('${k}')">Aplicar Modo</button>
                    </div>
                `;
            }).join('');
        }

        function renderPlaylist() {
            const playlist = currentConfig.rotation_playlist || [];
            const container = document.getElementById('playlist-container');
            let activeCount = 0;

            container.innerHTML = playlist.map((item, idx) => {
                const meta = tracksMetaMap[item.track_id] || {};
                const isHaruna = item.track_id === 'jpn_mharuna';
                if (item.enabled) activeCount++;

                return `
                    <div class="track-card ${item.enabled ? 'active' : 'inactive'}" id="card-track-${idx}">
                        <div class="track-info">
                            <input type="checkbox" id="chk-track-${idx}" ${item.enabled ? 'checked' : ''} onchange="onTrackToggle(${idx})">
                            <div>
                                <div class="track-title">${meta.name || item.track_id}</div>
                                <div class="track-sub">${meta.location || 'Oficial'} ${isHaruna ? '• ⚠️ Sprint P2P (1 volta)' : ''}</div>
                            </div>
                        </div>
                        <div class="track-laps-wrapper">
                            <input type="number" id="laps-track-${idx}" value="${item.laps}" min="1" max="99" 
                                class="track-laps-input form-control" 
                                ${isHaruna ? 'disabled value="1"' : ''}
                                onchange="onTrackLapsChange(${idx})">
                            <span style="font-size: 11px; color: var(--text-muted);">V</span>
                        </div>
                    </div>
                `;
            }).join('');

            document.getElementById('tracks-active-count').innerText = `${activeCount} de ${playlist.length} ativas`;
        }

        function onTrackToggle(idx) {
            const chk = document.getElementById(`chk-track-${idx}`);
            currentConfig.rotation_playlist[idx].enabled = chk.checked;
            const card = document.getElementById(`card-track-${idx}`);
            if (chk.checked) {
                card.classList.add('active');
                card.classList.remove('inactive');
            } else {
                card.classList.remove('active');
                card.classList.add('inactive');
            }
            updateActiveTrackCount();
        }

        function onTrackLapsChange(idx) {
            const input = document.getElementById(`laps-track-${idx}`);
            let val = parseInt(input.value) || 3;
            if (currentConfig.rotation_playlist[idx].track_id === 'jpn_mharuna') {
                val = 1;
                input.value = 1;
            }
            currentConfig.rotation_playlist[idx].laps = val;
        }

        function updateActiveTrackCount() {
            const count = (currentConfig.rotation_playlist || []).filter(t => t.enabled).length;
            document.getElementById('tracks-active-count').innerText = `${count} de ${(currentConfig.rotation_playlist || []).length} ativas`;
        }

        function setAllTracks(enable) {
            (currentConfig.rotation_playlist || []).forEach(t => t.enabled = enable);
            renderPlaylist();
        }

        function applyBatchLaps() {
            const val = parseInt(document.getElementById('batch-laps').value) || 3;
            (currentConfig.rotation_playlist || []).forEach(t => {
                if (t.track_id !== 'jpn_mharuna') {
                    t.laps = val;
                }
            });
            renderPlaylist();
            showToast(`Aplicado ${val} voltas em todos os circuitos!`);
        }

        function applyPreset(presetId) {
            const pr = presetsMap[presetId];
            if (!pr) return;

            // Merge server
            if (pr.server) {
                Object.assign(currentConfig.server, pr.server);
                document.getElementById('cfg-auto-start').value = String(pr.server.auto_start_enabled);
                document.getElementById('cfg-countdown').value = pr.server.countdown_seconds || 20;
                document.getElementById('cfg-rot-mode').value = pr.server.rotation_mode || 'sequential';
                document.getElementById('cfg-def-laps').value = pr.server.default_laps || 3;
                document.getElementById('srv-mode-badge').innerText = (pr.server.rotation_mode || 'sequential').toUpperCase();
            }

            // Merge powerups
            if (pr.powerup_options) {
                Object.assign(currentConfig.powerup_options, pr.powerup_options);
                document.getElementById('cfg-pw-respawn').value = pr.powerup_options.respawn_rate || 'Normal';
                renderPowerups();
            }

            // Merge advanced
            if (pr.advanced_options) {
                Object.assign(currentConfig.advanced_options, pr.advanced_options);
                document.getElementById('cfg-adv-damage').value = pr.advanced_options.damage || 'Medium';
                document.getElementById('cfg-adv-handicap').value = pr.advanced_options.handicap || 'High';
                document.getElementById('cfg-adv-respawn').checked = !!pr.advanced_options.respawn;
                document.getElementById('cfg-adv-timeout').checked = !!pr.advanced_options.timeout;
                document.getElementById('cfg-adv-mods').checked = !!pr.advanced_options.mods;
                document.getElementById('cfg-adv-upgrades').checked = !!pr.advanced_options.upgrades;
                document.getElementById('cfg-adv-ai').checked = !!pr.advanced_options.ai;
            }

            // Merge BoP
            if (pr.gameplay) {
                Object.assign(currentConfig.gameplay, pr.gameplay);
                document.getElementById('cfg-bop-enabled').checked = !!pr.gameplay.bop_enabled;
                if (pr.gameplay.bop_class_d_multiplier) document.getElementById('cfg-bop-d').value = pr.gameplay.bop_class_d_multiplier;
                if (pr.gameplay.bop_class_c_multiplier) document.getElementById('cfg-bop-c').value = pr.gameplay.bop_class_c_multiplier;
                if (pr.gameplay.bop_class_b_multiplier) document.getElementById('cfg-bop-b').value = pr.gameplay.bop_class_b_multiplier;
            }

            // Laps
            if (pr.playlist_laps) {
                (currentConfig.rotation_playlist || []).forEach(t => {
                    if (t.track_id !== 'jpn_mharuna') {
                        t.laps = pr.playlist_laps;
                    }
                });
                renderPlaylist();
            }

            showToast(`Preset "${pr.name}" carregado! Clique em Salvar para aplicar.`);
        }

        async function saveAllToServer() {
            // Coleta dados dos inputs para o config
            currentConfig.server.auto_start_enabled = document.getElementById('cfg-auto-start').value === 'true';
            currentConfig.server.countdown_seconds = parseInt(document.getElementById('cfg-countdown').value) || 20;
            currentConfig.server.rotation_mode = document.getElementById('cfg-rot-mode').value;
            currentConfig.server.default_laps = parseInt(document.getElementById('cfg-def-laps').value) || 3;

            currentConfig.powerup_options.respawn_rate = document.getElementById('cfg-pw-respawn').value;

            currentConfig.advanced_options.damage = document.getElementById('cfg-adv-damage').value;
            currentConfig.advanced_options.handicap = document.getElementById('cfg-adv-handicap').value;
            currentConfig.advanced_options.respawn = document.getElementById('cfg-adv-respawn').checked;
            currentConfig.advanced_options.timeout = document.getElementById('cfg-adv-timeout').checked;
            currentConfig.advanced_options.mods = document.getElementById('cfg-adv-mods').checked;
            currentConfig.advanced_options.upgrades = document.getElementById('cfg-adv-upgrades').checked;
            currentConfig.advanced_options.ai = document.getElementById('cfg-adv-ai').checked;

            currentConfig.gameplay.bop_enabled = document.getElementById('cfg-bop-enabled').checked;
            currentConfig.gameplay.bop_class_d_multiplier = parseFloat(document.getElementById('cfg-bop-d').value) || 1.48;
            currentConfig.gameplay.bop_class_c_multiplier = parseFloat(document.getElementById('cfg-bop-c').value) || 1.28;
            currentConfig.gameplay.bop_class_b_multiplier = parseFloat(document.getElementById('cfg-bop-b').value) || 1.14;

            try {
                const res = await fetch('/api/save_config', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(currentConfig)
                });
                const result = await res.json();
                if (result.success) {
                    showToast("✓ Configurações salvas e aplicadas ao servidor com sucesso!");
                    document.getElementById('srv-mode-badge').innerText = currentConfig.server.rotation_mode.toUpperCase();
                } else {
                    showToast("Erro ao salvar: " + (result.message || "Desconhecido"), true);
                }
            } catch (e) {
                showToast("Falha de conexão com o servidor!", true);
            }
        }

        async function fetchInitialData() {
            try {
                const res = await fetch('/api/stats');
                const data = await res.json();

                currentConfig = {
                    server: data.server || {},
                    powerup_options: data.powerup_options || {},
                    advanced_options: data.advanced_options || {},
                    gameplay: data.gameplay || {},
                    network: data.network || {},
                    rotation_playlist: data.rotation_playlist || []
                };

                presetsMap = data.presets || {};
                (data.tracks_meta || []).forEach(t => { tracksMetaMap[t.id] = t; });

                // Inicializa Inputs
                document.getElementById('cfg-auto-start').value = String(currentConfig.server.auto_start_enabled || false);
                document.getElementById('cfg-countdown').value = currentConfig.server.countdown_seconds || 20;
                document.getElementById('cfg-rot-mode').value = currentConfig.server.rotation_mode || 'sequential';
                document.getElementById('cfg-def-laps').value = currentConfig.server.default_laps || 3;
                document.getElementById('srv-mode-badge').innerText = (currentConfig.server.rotation_mode || 'sequential').toUpperCase();

                document.getElementById('cfg-pw-respawn').value = currentConfig.powerup_options.respawn_rate || 'Normal';

                document.getElementById('cfg-adv-damage').value = currentConfig.advanced_options.damage || 'Medium';
                document.getElementById('cfg-adv-handicap').value = currentConfig.advanced_options.handicap || 'High';
                document.getElementById('cfg-adv-respawn').checked = currentConfig.advanced_options.respawn !== false;
                document.getElementById('cfg-adv-timeout').checked = currentConfig.advanced_options.timeout !== false;
                document.getElementById('cfg-adv-mods').checked = currentConfig.advanced_options.mods !== false;
                document.getElementById('cfg-adv-upgrades').checked = currentConfig.advanced_options.upgrades !== false;
                document.getElementById('cfg-adv-ai').checked = !!currentConfig.advanced_options.ai;

                document.getElementById('cfg-bop-enabled').checked = currentConfig.gameplay.bop_enabled !== false;
                document.getElementById('cfg-bop-d').value = currentConfig.gameplay.bop_class_d_multiplier || 1.48;
                document.getElementById('cfg-bop-c').value = currentConfig.gameplay.bop_class_c_multiplier || 1.28;
                document.getElementById('cfg-bop-b').value = currentConfig.gameplay.bop_class_b_multiplier || 1.14;

                renderPresets();
                renderPowerups();
                renderPlaylist();
                updateLiveTelemetry(data);
            } catch (e) {
                console.error("Erro ao carregar dados:", e);
            }
        }

        async function updateTelemetryOnly() {
            try {
                const res = await fetch('/api/stats');
                const data = await res.json();
                updateLiveTelemetry(data);
            } catch (e) {}
        }

        function updateLiveTelemetry(data) {
            // Classificação
            const lb = data.leaderboard || [];
            const lbBody = document.getElementById('leaderboard-body');
            if (lb.length > 0) {
                lbBody.innerHTML = lb.map((p, idx) => `
                    <tr>
                        <td class="${idx === 0 ? 'rank-1' : idx === 1 ? 'rank-2' : idx === 2 ? 'rank-3' : ''}">#${idx + 1}</td>
                        <td><strong>${p.name}</strong></td>
                        <td>${p.total_races}</td>
                        <td>${p.wins}</td>
                        <td>${p.podiums}</td>
                        <td>${p.hits_dealt}</td>
                        <td>${p.wrecks_caused}</td>
                        <td>${p.mvp_awards}</td>
                        <td><span class="pts-badge">${p.points} PTS</span></td>
                    </tr>
                `).join('');
            }

            // Histórico de Partidas
            const matches = data.recent_matches || [];
            const mBody = document.getElementById('matches-body');
            if (matches.length > 0) {
                mBody.innerHTML = matches.map(m => `
                    <tr>
                        <td style="color: var(--text-muted);">${m.timestamp}</td>
                        <td><strong>${m.track_name}</strong></td>
                        <td>${m.laps}V</td>
                        <td>🥇 <strong>${m.winner_name || '--'}</strong></td>
                        <td>${m.total_players}</td>
                        <td>⭐ <span style="color: var(--cyan);">${m.mvp_name || '--'}</span></td>
                    </tr>
                `).join('');
            }

            // Feed de Combate
            const tel = data.telemetry || {};
            const hits = tel.hits_summary || {};
            const feed = document.getElementById('combat-feed');
            const hitKeys = Object.keys(hits);
            if (hitKeys.length > 0) {
                feed.innerHTML = hitKeys.map(k => `
                    <div style="display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid rgba(255,255,255,0.05); font-size: 13px;">
                        <span>🎯 <strong>${k}</strong> acertou</span>
                        <span style="color: var(--pink); font-weight: 700;">${hits[k]} tiros</span>
                    </div>
                `).join('');
            }

            // Matriz de Combate
            const cMatrix = data.combat_matrix || [];
            const cBody = document.getElementById('combat-matrix-body');
            if (cMatrix.length > 0) {
                cBody.innerHTML = cMatrix.map(c => `
                    <tr>
                        <td><strong>${c.attacker}</strong></td>
                        <td style="color: var(--pink);">➔</td>
                        <td><strong>${c.victim}</strong></td>
                        <td><span style="color: var(--cyan); font-weight: 700;">${c.weapon}</span></td>
                        <td><span class="pts-badge" style="background: rgba(255, 0, 127, 0.15); color: var(--pink);">${c.total_hits} tiros</span></td>
                    </tr>
                `).join('');
            }

            document.getElementById('last-update').innerText = 'Atualizado em ' + new Date().toLocaleTimeString();
        }

        fetchInitialData();
        setInterval(updateTelemetryOnly, 4000);
    </script>
</body>
</html>
"""


class BlurMTXHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/" or url.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode("utf-8"))
        elif url.path == "/api/stats":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            data = get_current_server_status()
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        url = urlparse(self.path)
        if url.path == "/api/save_config":
            try:
                length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(length).decode("utf-8")
                new_cfg = json.loads(body)

                # Mantém proteções (Monte Haruna P2P sprint mantido em 1 volta)
                for item in new_cfg.get("rotation_playlist", []):
                    if item.get("track_id") == "jpn_mharuna":
                        item["laps"] = 1

                # Salva no disco
                save_config_safe(new_cfg)

                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "message": "Salvo com sucesso"}).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "message": str(e)}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        return


def run_web_server(port=PORT):
    server = HTTPServer(("0.0.0.0", port), BlurMTXHandler)
    print(f"=====================================================================")
    print(f"  ⚡ BlurMTX Web Dashboard rodando em:")
    print(f"  -> Local:   http://localhost:{port}")
    print(f"  -> Na Rede: http://<SEU_IP_LAN>:{port}")
    print(f"=====================================================================")
    server.serve_forever()


if __name__ == "__main__":
    run_web_server()
