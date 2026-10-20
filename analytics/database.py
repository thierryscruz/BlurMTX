"""
=============================================================================
BlurMTX — Database & Analytics Engine (SQLite)
=============================================================================
Gerencia a persistência de todas as corridas, ranking geral dos pilotos,
matriz de combate ("quem atirou em quem"), Hall da Fama e histórico de rivalidades.
Zero dependências externas (utiliza o sqlite3 nativo do Python).
=============================================================================
"""

import sqlite3
import json
import time
import sys
from pathlib import Path
from datetime import datetime

# Garante suporte a UTF-8 no terminal Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "blur_mtx.db"

# Pontuação oficial estilo Fórmula 1 para o Top 10
F1_POINTS = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Cria todas as tabelas necessárias no banco local SQLite."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 1. Tabela de Pilotos / Jogadores
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                total_races INTEGER DEFAULT 0,
                wins INTEGER DEFAULT 0,
                podiums INTEGER DEFAULT 0,
                points INTEGER DEFAULT 0,
                elo_rating INTEGER DEFAULT 1200,
                hits_dealt INTEGER DEFAULT 0,
                hits_taken INTEGER DEFAULT 0,
                wrecks_caused INTEGER DEFAULT 0,
                wrecks_suffered INTEGER DEFAULT 0,
                shields_used INTEGER DEFAULT 0,
                mvp_awards INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 2. Tabela de Corridas (Matches)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                track_id TEXT NOT NULL,
                track_name TEXT NOT NULL,
                laps INTEGER DEFAULT 3,
                winner_name TEXT,
                total_players INTEGER DEFAULT 0,
                mvp_name TEXT,
                most_aggressive TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 3. Tabela de Resultados por Corrida
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS match_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id INTEGER NOT NULL,
                player_name TEXT NOT NULL,
                position INTEGER NOT NULL,
                points_earned INTEGER DEFAULT 0,
                hits_dealt INTEGER DEFAULT 0,
                hits_taken INTEGER DEFAULT 0,
                wrecks_caused INTEGER DEFAULT 0,
                car_used TEXT,
                best_lap_time REAL,
                FOREIGN KEY (match_id) REFERENCES matches (id)
            )
        """)

        # 4. Matriz de Combate ("Quem atirou em quem")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS combat_matrix (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id INTEGER,
                attacker TEXT NOT NULL,
                victim TEXT NOT NULL,
                weapon TEXT NOT NULL,
                hits_count INTEGER DEFAULT 1,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 5. Hall da Fama de Melhores Voltas por Pista
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS track_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                track_id TEXT NOT NULL,
                track_name TEXT NOT NULL,
                player_name TEXT NOT NULL,
                car_name TEXT NOT NULL,
                best_lap_time REAL NOT NULL,
                date_achieved TEXT NOT NULL,
                UNIQUE(track_id)
            )
        """)

        conn.commit()


def process_match_telemetry(telemetry_data):
    """
    Processa os dados de uma partida encerrada (telemetry_last_match.json):
    - Computa posições e pontos no ranking geral
    - Calcula MVP e premiações especiais
    - Atualiza a matriz de combate e estatísticas dos jogadores
    """
    init_database()
    
    timestamp = telemetry_data.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    track_id = telemetry_data.get("track_id", "unknown_track")
    track_name = telemetry_data.get("track_name", track_id)
    laps = int(telemetry_data.get("laps", 3))
    
    results = telemetry_data.get("results", [])
    hits_summary = telemetry_data.get("hits_summary", {})
    wrecks_summary = telemetry_data.get("wrecks_summary", {})
    matrix_events = telemetry_data.get("combat_events", [])

    # Se results estiver vazio, infere pilotos a partir dos eventos de hits e wrecks
    if not results:
        active_names = set(hits_summary.keys()) | set(wrecks_summary.keys())
        if not active_names:
            active_names = {"Host", "Piloto_2"}
        results = [{"name": name, "position": idx + 1} for idx, name in enumerate(sorted(active_names))]

    winner_name = results[0]["name"] if results else "Desconhecido"

    # Determina Prêmios Especiais da Corrida
    # 1. MVP: maior pontuação combinada (Posição + Acertos + Wrecks)
    mvp_name = None
    best_mvp_score = -1
    for r in results:
        pname = r["name"]
        pos = r.get("position", 10)
        pos_pts = F1_POINTS[pos - 1] if pos <= len(F1_POINTS) else 0
        hits = hits_summary.get(pname, 0)
        wrecks = wrecks_summary.get(pname, 0)
        score = (pos_pts * 2) + (hits * 3) + (wrecks * 10)
        if score > best_mvp_score:
            best_mvp_score = score
            mvp_name = pname

    # 2. O Demolidor / Mais Agressivo
    most_aggressive = None
    max_hits = -1
    for pname, hits in hits_summary.items():
        if hits > max_hits:
            max_hits = hits
            most_aggressive = pname

    with get_db() as conn:
        cursor = conn.cursor()

        # Insere a corrida
        cursor.execute("""
            INSERT INTO matches (timestamp, track_id, track_name, laps, winner_name, total_players, mvp_name, most_aggressive)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (timestamp, track_id, track_name, laps, winner_name, len(results), mvp_name, most_aggressive))
        
        match_id = cursor.lastrowid

        # Insere resultados individuais e atualiza pontuação global
        for r in results:
            pname = r["name"]
            pos = r.get("position", 99)
            pts = F1_POINTS[pos - 1] if pos <= len(F1_POINTS) else 0
            hits_d = hits_summary.get(pname, 0)
            wrecks_c = wrecks_summary.get(pname, 0)
            car = r.get("car", "Corvette ZR1")
            lap_t = r.get("best_lap", None)

            cursor.execute("""
                INSERT INTO match_results (match_id, player_name, position, points_earned, hits_dealt, wrecks_caused, car_used, best_lap_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (match_id, pname, pos, pts, hits_d, wrecks_c, car, lap_t))

            # Atualiza ou insere jogador
            is_win = 1 if pos == 1 else 0
            is_podium = 1 if pos <= 3 else 0
            is_mvp = 1 if pname == mvp_name else 0

            cursor.execute("""
                INSERT INTO players (name, total_races, wins, podiums, points, hits_dealt, wrecks_caused, mvp_awards, last_seen)
                VALUES (?, 1, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(name) DO UPDATE SET
                    total_races = total_races + 1,
                    wins = wins + excluded.wins,
                    podiums = podiums + excluded.podiums,
                    points = points + excluded.points,
                    hits_dealt = hits_dealt + excluded.hits_dealt,
                    wrecks_caused = wrecks_caused + excluded.wrecks_caused,
                    mvp_awards = mvp_awards + excluded.mvp_awards,
                    last_seen = CURRENT_TIMESTAMP
            """, (pname, is_win, is_podium, pts, hits_d, wrecks_c, is_mvp))

        # Registra eventos da matriz de combate
        for ev in matrix_events:
            cursor.execute("""
                INSERT INTO combat_matrix (match_id, attacker, victim, weapon, hits_count)
                VALUES (?, ?, ?, ?, ?)
            """, (match_id, ev.get("attacker", "Host"), ev.get("victim", "Rival"), ev.get("weapon", "Shunt"), ev.get("count", 1)))

        conn.commit()

    return {
        "match_id": match_id,
        "winner": winner_name,
        "mvp": mvp_name,
        "most_aggressive": most_aggressive,
        "total_players": len(results)
    }


def get_leaderboard():
    """Retorna o Ranking Geral dos Pilotos ordenado por pontos e vitórias."""
    init_database()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name, total_races, wins, podiums, points, hits_dealt, wrecks_caused, mvp_awards
            FROM players
            ORDER BY points DESC, wins DESC, podiums DESC
        """)
        return [dict(row) for row in cursor.fetchall()]


def get_recent_matches(limit=10):
    """Retorna o histórico das corridas mais recentes."""
    init_database()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, timestamp, track_name, laps, winner_name, total_players, mvp_name
            FROM matches
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))
        return [dict(row) for row in cursor.fetchall()]


def get_combat_rivalry(player_a, player_b):
    """Calcula o confronto direto (head-to-head) entre dois pilotos."""
    init_database()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT attacker, SUM(hits_count) as total_hits
            FROM combat_matrix
            WHERE (attacker = ? AND victim = ?) OR (attacker = ? AND victim = ?)
            GROUP BY attacker
        """, (player_a, player_b, player_b, player_a))
        
        rivalry = {player_a: 0, player_b: 0}
        for row in cursor.fetchall():
            rivalry[row["attacker"]] = row["total_hits"]
        return rivalry


def get_all_combat_matrix():
    """Retorna os principais confrontos de combate (quem mais atirou em quem)."""
    init_database()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT attacker, victim, weapon, SUM(hits_count) as total_hits
            FROM combat_matrix
            GROUP BY attacker, victim, weapon
            ORDER BY total_hits DESC
            LIMIT 15
        """)
        return [dict(row) for row in cursor.fetchall()]


def seed_demo_data():
    """Insere dados de exemplo no SQLite para demonstrar o dashboard em funcionamento."""
    init_database()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM players")
        if cursor.fetchone()["count"] > 0:
            return  # Já tem dados

    # Simula 2 partidas para ilustrar o ranking e a telemetria
    sample_match_1 = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "track_id": "spa_barcelona_gracia",
        "track_name": "Barcelona — Gràcia",
        "laps": 3,
        "results": [
            {"name": "Thierry", "position": 1, "car": "Opel Astra Extreme"},
            {"name": "Piloto_2", "position": 2, "car": "Corvette ZR1"},
            {"name": "Piloto_3", "position": 3, "car": "VW Beetle (Fusca BoP)"},
            {"name": "Piloto_4", "position": 4, "car": "BMW M3 E92"}
        ],
        "hits_summary": {"Thierry": 14, "Piloto_2": 9, "Piloto_3": 11, "Piloto_4": 4},
        "wrecks_summary": {"Thierry": 2, "Piloto_3": 1},
        "combat_events": [
            {"attacker": "Thierry", "victim": "Piloto_2", "weapon": "Shunt", "count": 6},
            {"attacker": "Piloto_3", "victim": "Thierry", "weapon": "Bolt", "count": 5},
            {"attacker": "Piloto_2", "victim": "Piloto_4", "weapon": "Mine", "count": 4},
            {"attacker": "Thierry", "victim": "Piloto_3", "weapon": "Barge", "count": 3}
        ]
    }
    process_match_telemetry(sample_match_1)


if __name__ == "__main__":
    init_database()
    seed_demo_data()
    print("✓ Banco de dados blur_mtx.db inicializado e verificado com sucesso!")
