"""
=============================================================================
BlurMTX Server Control Panel
=============================================================================
Interface gráfica moderna para gerenciar o Servidor Dedicado do Blur (2010):
- Rotação Automática de Pistas (Checklist completo de mapas com voltas configuráveis)
- Power-up Options (Nitro, Shunt, Bolt, Shield, etc. individuais como no jogo)
- Advanced Options (Damage, Respawn, Handicap, Timeout, Mods, Upgrades, AI)
- Balance of Performance (BoP) & Garagem Multi-Class
- Configuração de Rede Unicast / Anti-Bloqueio de Firewall
- Telemetria de Combate e Webhooks do Discord
=============================================================================
"""

import os
import sys
import json
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "blur_mtx.json"
TRACKS_PATH = BASE_DIR / "tracks.json"
PRESETS_PATH = BASE_DIR / "presets.json"

# =============================================================================
# Paleta de Cores Neon (Inspirada no visual oficial do Blur)
# =============================================================================
C = {
    "bg":            "#0c0f17",
    "surface":       "#151a26",
    "surface2":      "#1e2538",
    "surface_card":  "#1b2233",
    "border":        "#2b364e",
    "accent_cyan":   "#00d2ff",
    "accent_pink":   "#ff007f",
    "accent_orange": "#ff6b00",
    "text":          "#f0f4fc",
    "text_muted":    "#8796b4",
    "green":         "#10b981",
    "red":           "#ef4444",
    # Cores dos Power-ups do Blur
    "pw_nitro":      "#22c55e",
    "pw_barge":      "#c084fc",
    "pw_shunt":      "#ef4444",
    "pw_bolt":       "#f472b6",
    "pw_repair":     "#eab308",
    "pw_shield":     "#38bdf8",
    "pw_mine":       "#fb923c",
    "pw_shock":      "#60a5fa",
}

FONT_TITLE = ("Segoe UI Bold", 14)
FONT_SECTION = ("Segoe UI Semibold", 11)
FONT_MAIN = ("Segoe UI", 10)
FONT_SMALL = ("Segoe UI", 9)
FONT_BOLD = ("Segoe UI Bold", 10)


def load_tracks():
    if TRACKS_PATH.exists():
        try:
            with open(TRACKS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []


def load_config():
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_config(cfg):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


class BlurMTXControlApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BlurMTX — Dedicated Server & Gameplay Manager")
        self.geometry("900x740")
        self.minsize(840, 660)
        self.configure(bg=C["bg"])

        # Centraliza na tela
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        w, h = 900, 740
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

        self.tracks_data = load_tracks()
        self.tracks_by_id = {t["id"]: t for t in self.tracks_data}
        self.cfg = load_config()

        # Estrutura para os itens do checklist de pistas: list of dicts
        self.track_items = []

        self._build_style()
        self._build_header()
        self._build_presets_bar()
        self._build_notebook()
        self._build_footer()

    def _build_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure("TNotebook", background=C["bg"], borderwidth=0)
        style.configure("TNotebook.Tab",
            background=C["surface"],
            foreground=C["text_muted"],
            padding=(16, 9),
            font=FONT_SECTION,
            borderwidth=0
        )
        style.map("TNotebook.Tab",
            background=[("selected", C["surface2"])],
            foreground=[("selected", C["accent_cyan"])],
        )

        style.configure("TCombobox",
            fieldbackground=C["surface2"],
            background=C["surface2"],
            foreground=C["text"],
            arrowcolor=C["accent_cyan"],
            borderwidth=1,
        )

    def _build_header(self):
        header = tk.Frame(self, bg=C["bg"], pady=10, padx=20)
        header.pack(fill="x")

        title_box = tk.Frame(header, bg=C["bg"])
        title_box.pack(side="left")

        tk.Label(title_box, text="⚡ BlurMTX", font=("Segoe UI Black", 18), bg=C["bg"], fg=C["accent_cyan"]).pack(side="left")
        tk.Label(title_box, text="  Dedicated Server & Match Controller", font=FONT_TITLE, bg=C["bg"], fg=C["text"]).pack(side="left", padx=(4, 0))

        tk.Label(header, text="v1.2.0", font=FONT_SMALL, bg=C["surface2"], fg=C["accent_pink"], padx=8, pady=2).pack(side="right")

    def _build_presets_bar(self):
        bar = tk.Frame(self, bg=C["surface"], padx=16, pady=8, highlightthickness=1, highlightbackground=C["border"])
        bar.pack(fill="x", padx=16, pady=(0, 10))

        tk.Label(bar, text="⚡ Presets Rápidos (1-Clique):", font=FONT_BOLD, bg=C["surface"], fg=C["accent_cyan"]).pack(side="left", padx=(0, 10))

        presets = [
            ("f1_grand_prix", "🏆 F1 Grand Prix", C["accent_orange"]),
            ("demolition_derby", "💣 Caos Demolition", C["accent_pink"]),
            ("clean_racing", "🚀 Pura Velocidade", C["green"]),
            ("bop_multiclass", "🏎️ Clássicos BoP", C["accent_cyan"]),
            ("blur_default", "⚡ Blur Padrão", C["text"]),
        ]

        for pid, label, col in presets:
            tk.Button(bar, text=label, command=lambda p=pid: self._apply_preset_gui(p),
                      bg=C["surface2"], fg=col, activebackground=C["border"], activeforeground=col,
                      relief="flat", padx=10, pady=3, font=FONT_SMALL).pack(side="left", padx=3)

    def _apply_preset_gui(self, pid):
        if not PRESETS_PATH.exists():
            return
        try:
            with open(PRESETS_PATH, "r", encoding="utf-8") as f:
                presets = json.load(f)
        except Exception:
            return

        pr = presets.get(pid)
        if not pr:
            return

        # Server
        srv = pr.get("server", {})
        if "auto_start_enabled" in srv: self.v_auto_start.set(srv["auto_start_enabled"])
        if "countdown_seconds" in srv: self.v_countdown.set(srv["countdown_seconds"])
        if "rotation_mode" in srv: self.v_rot_mode.set(srv["rotation_mode"])
        if "default_laps" in srv: self.v_def_laps.set(srv["default_laps"])

        # Powerups
        pw = pr.get("powerup_options", {})
        if "nitro" in pw: self.v_pw_nitro.set(pw["nitro"])
        if "barge" in pw: self.v_pw_barge.set(pw["barge"])
        if "shunt" in pw: self.v_pw_shunt.set(pw["shunt"])
        if "bolt" in pw: self.v_pw_bolt.set(pw["bolt"])
        if "repair" in pw: self.v_pw_repair.set(pw["repair"])
        if "shield" in pw: self.v_pw_shield.set(pw["shield"])
        if "mine" in pw: self.v_pw_mine.set(pw["mine"])
        if "shock" in pw: self.v_pw_shock.set(pw["shock"])
        if "respawn_rate" in pw: self.v_pw_respawn.set(pw["respawn_rate"])

        # Advanced
        adv = pr.get("advanced_options", {})
        if "damage" in adv: self.v_adv_damage.set(adv["damage"])
        if "respawn" in adv: self.v_adv_respawn.set(adv["respawn"])
        if "handicap" in adv: self.v_adv_handicap.set(adv["handicap"])
        if "timeout" in adv: self.v_adv_timeout.set(adv["timeout"])
        if "mods" in adv: self.v_adv_mods.set(adv["mods"])
        if "upgrades" in adv: self.v_adv_upgrades.set(adv["upgrades"])
        if "ai" in adv: self.v_adv_ai.set(adv["ai"])

        # BoP
        gp = pr.get("gameplay", {})
        if "bop_enabled" in gp: self.v_bop.set(gp["bop_enabled"])
        if "bop_class_d_multiplier" in gp: self.v_bop_d.set(gp["bop_class_d_multiplier"])
        if "bop_class_c_multiplier" in gp: self.v_bop_c.set(gp["bop_class_c_multiplier"])
        if "bop_class_b_multiplier" in gp: self.v_bop_b.set(gp["bop_class_b_multiplier"])

        # Playlist laps
        if "playlist_laps" in pr:
            lval = str(pr["playlist_laps"])
            for item in self.track_items:
                if not item.get("is_sprint"):
                    item["var_laps"].set(lval)

        self.lbl_status.config(text=f"✓ Preset '{pr.get('name')}' carregado com sucesso! Clique em 'Salvar Configurações' para aplicar.", fg=C["accent_cyan"])

    def _build_notebook(self):
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True, padx=16, pady=(0, 10))

        self.tab_rotation = tk.Frame(self.nb, bg=C["surface2"], padx=14, pady=14)
        self.tab_powerups = tk.Frame(self.nb, bg=C["surface2"], padx=14, pady=14)
        self.tab_advanced = tk.Frame(self.nb, bg=C["surface2"], padx=14, pady=14)
        self.tab_bop      = tk.Frame(self.nb, bg=C["surface2"], padx=14, pady=14)
        self.tab_network  = tk.Frame(self.nb, bg=C["surface2"], padx=14, pady=14)
        self.tab_combat   = tk.Frame(self.nb, bg=C["surface2"], padx=14, pady=14)

        self.nb.add(self.tab_rotation, text=" 🏁 Rotação de Pistas ")
        self.nb.add(self.tab_powerups, text=" ⚡ Power-ups ")
        self.nb.add(self.tab_advanced, text=" ⚙️ Opções Avançadas ")
        self.nb.add(self.tab_bop,      text=" 🏎️ BoP & Multi-Class ")
        self.nb.add(self.tab_network,  text=" 🌐 Conexão & LAN ")
        self.nb.add(self.tab_combat,   text=" 🎯 Combate & Discord ")

        self._init_tab_rotation()
        self._init_tab_powerups()
        self._init_tab_advanced()
        self._init_tab_bop()
        self._init_tab_network()
        self._init_tab_combat()

    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------
    # ABA 1: ROTAÇÃO DE PISTAS (CHECKLIST COMPLETO COM QUANTIDADE DE VOLTAS)
    # -------------------------------------------------------------------------
    def _init_tab_rotation(self):
        t = self.tab_rotation
        srv = self.cfg.get("server", {})

        top_opts = tk.Frame(t, bg=C["surface2"], padx=12, pady=10, highlightthickness=1, highlightbackground=C["border"])
        top_opts.pack(fill="x", pady=(0, 10))

        self.v_auto_rot   = tk.BooleanVar(value=srv.get("auto_rotation_enabled", True))
        self.v_auto_start = tk.BooleanVar(value=srv.get("auto_start_enabled", True))
        self.v_rot_mode   = tk.StringVar(value=srv.get("rotation_mode", "sequential"))
        self.v_countdown  = tk.IntVar(value=srv.get("countdown_seconds", 20))
        self.v_def_laps   = tk.IntVar(value=srv.get("default_laps", 3))
        self.v_batch_laps = tk.StringVar(value="3")

        # Linha 1: Rotação de Mapas
        row1 = tk.Frame(top_opts, bg=C["surface2"])
        row1.pack(fill="x")

        tk.Checkbutton(row1, text="Ativar Rotação Automática de Pistas (Map Rotation)",
                       variable=self.v_auto_rot, bg=C["surface2"], fg=C["text"],
                       selectcolor=C["surface"], activebackground=C["surface2"],
                       activeforeground=C["accent_cyan"], font=FONT_BOLD).pack(side="left")

        tk.Label(row1, text="|  Ordem:", font=FONT_MAIN, bg=C["surface2"], fg=C["text_muted"]).pack(side="left", padx=(16, 6))
        tk.Radiobutton(row1, text="Sequencial", variable=self.v_rot_mode, value="sequential",
                       bg=C["surface2"], fg=C["text"], selectcolor=C["surface"],
                       activebackground=C["surface2"], activeforeground=C["accent_cyan"], font=FONT_SMALL).pack(side="left")
        tk.Radiobutton(row1, text="Aleatório (Shuffle)", variable=self.v_rot_mode, value="random",
                       bg=C["surface2"], fg=C["text"], selectcolor=C["surface"],
                       activebackground=C["surface2"], activeforeground=C["accent_cyan"], font=FONT_SMALL).pack(side="left", padx=4)

        tk.Label(row1, text="|  Voltas Padrão:", font=FONT_MAIN, bg=C["surface2"], fg=C["text_muted"]).pack(side="left", padx=(16, 6))
        tk.Spinbox(row1, from_=1, to=99, textvariable=self.v_def_laps, width=3, font=FONT_MAIN,
                   bg=C["surface"], fg=C["text"], insertbackground=C["text"], justify="center").pack(side="left")

        # Linha 2: Modo de Start da Partida (Automático vs Manual)
        row2 = tk.Frame(top_opts, bg=C["surface2"])
        row2.pack(fill="x", pady=(10, 2))

        tk.Label(row2, text="Modo de Início da Corrida:", font=FONT_BOLD, bg=C["surface2"], fg=C["accent_cyan"]).pack(side="left", padx=(0, 10))

        tk.Radiobutton(row2, text="⏱️ Start Automático (Countdown)", variable=self.v_auto_start, value=True,
                       bg=C["surface2"], fg=C["text"], selectcolor=C["surface"],
                       activebackground=C["surface2"], activeforeground=C["accent_cyan"], font=FONT_MAIN).pack(side="left")

        tk.Radiobutton(row2, text="🎮 Start Manual (Aguardar Host dar Start)", variable=self.v_auto_start, value=False,
                       bg=C["surface2"], fg=C["text"], selectcolor=C["surface"],
                       activebackground=C["surface2"], activeforeground=C["accent_cyan"], font=FONT_MAIN).pack(side="left", padx=(12, 0))

        tk.Label(row2, text="|  Tempo no Lobby:", font=FONT_MAIN, bg=C["surface2"], fg=C["text_muted"]).pack(side="left", padx=(16, 6))
        tk.Spinbox(row2, from_=5, to=120, textvariable=self.v_countdown, width=4, font=FONT_MAIN,
                   bg=C["surface"], fg=C["text"], insertbackground=C["text"], justify="center").pack(side="left")
        tk.Label(row2, text="seg", font=FONT_SMALL, bg=C["surface2"], fg=C["text_muted"]).pack(side="left", padx=(3, 0))

        # Linha 3: Nota explicativa para tirar qualquer dúvida sobre o Start Manual
        row3 = tk.Frame(top_opts, bg=C["surface2"])
        row3.pack(fill="x", pady=(4, 0))
        tk.Label(row3, text="💡 Dica: No Start Manual, o BlurMTX preenche a pista e as voltas certas na tela do host automaticamente, mas NÃO dá largada sozinho. O host pode esperar quem caiu se reconectar e apertar Start na hora certa!",
                 font=("Segoe UI Italic", 8), bg=C["surface2"], fg=C["accent_cyan"]).pack(anchor="w")

        # Barra de Ações Rápidas do Checklist
        action_bar = tk.Frame(t, bg=C["surface"], padx=10, pady=6, highlightthickness=1, highlightbackground=C["border"])
        action_bar.pack(fill="x", pady=(8, 4))

        tk.Label(action_bar, text="Checklist de Mapas:", font=FONT_BOLD, bg=C["surface"], fg=C["accent_cyan"]).pack(side="left", padx=(0, 8))

        tk.Button(action_bar, text="✓ Marcar Todos", command=self._check_all_tracks, bg=C["surface2"], fg=C["text"],
                  relief="flat", padx=6, pady=2, font=FONT_SMALL).pack(side="left", padx=2)
        tk.Button(action_bar, text="✗ Desmarcar Todos", command=self._uncheck_all_tracks, bg=C["surface2"], fg=C["text_muted"],
                  relief="flat", padx=6, pady=2, font=FONT_SMALL).pack(side="left", padx=2)

        tk.Label(action_bar, text="|  Voltas em Lote:", font=FONT_SMALL, bg=C["surface"], fg=C["text_muted"]).pack(side="left", padx=(8, 4))
        for lp in [2, 3, 5, 10, 15]:
            tk.Button(action_bar, text=f"{lp}V", command=lambda n=lp: self._set_all_laps(n), bg=C["surface2"], fg=C["accent_cyan"],
                      relief="flat", padx=5, pady=2, font=FONT_SMALL).pack(side="left", padx=1)

        tk.Label(action_bar, text="Personalizar:", font=FONT_SMALL, bg=C["surface"], fg=C["text_muted"]).pack(side="left", padx=(6, 2))
        tk.Spinbox(action_bar, from_=1, to=99, textvariable=self.v_batch_laps, width=3, font=FONT_SMALL,
                   bg=C["surface2"], fg=C["text"], insertbackground=C["text"], justify="center").pack(side="left")
        tk.Button(action_bar, text="Aplicar a Todos", command=self._apply_batch_laps, bg=C["surface2"], fg=C["green"],
                  relief="flat", padx=6, pady=2, font=FONT_SMALL).pack(side="left", padx=(3, 0))

        self.lbl_track_counter = tk.Label(action_bar, text="", font=FONT_BOLD, bg=C["surface"], fg=C["accent_cyan"])
        self.lbl_track_counter.pack(side="right", padx=10)

        # Cabeçalho da Tabela do Checklist
        header_bar = tk.Frame(t, bg=C["surface2"], padx=8, pady=5, highlightthickness=1, highlightbackground=C["border"])
        header_bar.pack(fill="x", pady=(2, 4))

        tk.Label(header_bar, text="Ordem", font=FONT_BOLD, bg=C["surface2"], fg=C["text_muted"], width=6, anchor="w").pack(side="left", padx=4)
        tk.Label(header_bar, text="Pista Oficial & Localização", font=FONT_BOLD, bg=C["surface2"], fg=C["text_muted"], anchor="w").pack(side="left", padx=10)
        tk.Label(header_bar, text="Qtd. de Voltas (Digitável: 1 a 99)", font=FONT_BOLD, bg=C["surface2"], fg=C["accent_cyan"], anchor="e").pack(side="right", padx=16)
        tk.Label(header_bar, text="Tipo", font=FONT_BOLD, bg=C["surface2"], fg=C["text_muted"], anchor="e").pack(side="right", padx=24)

        # Container Rolável para o Checklist de Pistas
        list_container = tk.Frame(t, bg=C["surface"], highlightthickness=1, highlightbackground=C["border"])
        list_container.pack(fill="both", expand=True)

        self.canvas_tracks = tk.Canvas(list_container, bg=C["surface"], borderwidth=0, highlightthickness=0)
        v_scroll = tk.Scrollbar(list_container, orient="vertical", command=self.canvas_tracks.yview)
        self.canvas_tracks.configure(yscrollcommand=v_scroll.set)

        v_scroll.pack(side="right", fill="y")
        self.canvas_tracks.pack(side="left", fill="both", expand=True)

        self.tracks_inner_frame = tk.Frame(self.canvas_tracks, bg=C["surface"])
        self.canvas_window = self.canvas_tracks.create_window((0, 0), window=self.tracks_inner_frame, anchor="nw")

        self.tracks_inner_frame.bind("<Configure>", lambda e: self.canvas_tracks.configure(scrollregion=self.canvas_tracks.bbox("all")))
        self.canvas_tracks.bind("<Configure>", lambda e: self.canvas_tracks.itemconfig(self.canvas_window, width=e.width))

        # Suporte ao scroll do mouse
        self.canvas_tracks.bind_all("<MouseWheel>", self._on_mousewheel)

        self._populate_track_checklist()

    def _on_mousewheel(self, event):
        if self.canvas_tracks.winfo_exists():
            self.canvas_tracks.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _update_track_counter(self):
        active_cnt = sum(1 for item in self.track_items if item["var_enabled"].get())
        total_cnt = len(self.track_items)
        self.lbl_track_counter.config(text=f"📍 {active_cnt} de {total_cnt} pistas ativas")

    def _populate_track_checklist(self):
        # Limpa widgets anteriores
        for widget in self.tracks_inner_frame.winfo_children():
            widget.destroy()
        self.track_items.clear()

        # Lê a lista atual salva no JSON (ou cria a partir de tracks_data)
        saved_list = self.cfg.get("rotation_playlist", [])
        saved_dict = {}

        # Suporta tanto formato novo [{track_id, enabled, laps}] quanto antigo ["id1", "id2"]
        for item in saved_list:
            if isinstance(item, dict):
                saved_dict[item.get("track_id")] = item
            elif isinstance(item, str):
                saved_dict[item] = {"track_id": item, "enabled": True, "laps": 3}

        # Organiza a ordem dos mapas conforme a playlist salva
        ordered_tracks = []
        seen = set()

        # Primeiro os que já estavam na playlist
        for item in saved_list:
            tid = item.get("track_id") if isinstance(item, dict) else item
            if tid in self.tracks_by_id and tid not in seen:
                ordered_tracks.append(self.tracks_by_id[tid])
                seen.add(tid)

        # Depois o restante das 18 pistas
        for t in self.tracks_data:
            if t["id"] not in seen:
                ordered_tracks.append(t)
                seen.add(t["id"])

        # Renderiza a lista de pistas no frame rolável
        for idx, trk in enumerate(ordered_tracks):
            tid = trk["id"]
            saved_info = saved_dict.get(tid, {})
            is_enabled = saved_info.get("enabled", True)
            laps_val = saved_info.get("laps", trk.get("default_laps", 3))

            var_enabled = tk.BooleanVar(value=is_enabled)
            var_laps = tk.StringVar(value=str(laps_val))

            # Listener para atualizar contador em tempo real
            var_enabled.trace_add("write", lambda *args: self._update_track_counter())

            row = tk.Frame(self.tracks_inner_frame, bg=C["surface2"] if idx % 2 == 0 else C["surface"], padx=8, pady=4)
            row.pack(fill="x", padx=4, pady=1)

            # Botões de Reordenação
            btn_box = tk.Frame(row, bg=row["bg"], width=50)
            btn_box.pack(side="left")
            btn_up = tk.Button(btn_box, text="▲", command=lambda i=idx: self._move_track_row(i, -1),
                               bg=C["surface"], fg=C["text_muted"], relief="flat", width=2, font=("Segoe UI", 8))
            btn_up.pack(side="left", padx=1)
            btn_dn = tk.Button(btn_box, text="▼", command=lambda i=idx: self._move_track_row(i, 1),
                               bg=C["surface"], fg=C["text_muted"], relief="flat", width=2, font=("Segoe UI", 8))
            btn_dn.pack(side="left", padx=1)

            # Checkbox com o nome da pista
            display_title = f"{trk['name']} ({trk.get('location', '')})"
            cb = tk.Checkbutton(row, text=display_title, variable=var_enabled, font=FONT_MAIN,
                                bg=row["bg"], fg=C["text"], selectcolor=C["surface"],
                                activebackground=row["bg"], activeforeground=C["accent_cyan"])
            cb.pack(side="left", padx=6)

            # Lado Direito: Seletor de Voltas (Laps) Digitável e Tag de Tipo de Pista
            is_sprint = (trk.get("type") == "sprint" or trk.get("max_laps") == 1)

            laps_box = tk.Frame(row, bg=row["bg"])
            laps_box.pack(side="right", padx=6)

            tk.Label(laps_box, text="Voltas:", font=FONT_SMALL, bg=row["bg"], fg=C["text_muted"]).pack(side="left", padx=(0, 4))
            
            # Campo Spinbox DIGITÁVEL para voltas
            sb_laps = tk.Spinbox(laps_box, from_=1, to=99, textvariable=var_laps, width=3,
                                 font=FONT_BOLD, bg=C["surface"], fg=C["text"],
                                 buttonbackground=C["surface2"], insertbackground=C["text"],
                                 justify="center")
            sb_laps.pack(side="left")

            if is_sprint:
                tk.Label(laps_box, text="(Sprint P2P • 1 volta recomendada)",
                         font=("Segoe UI", 8), bg=row["bg"], fg=C["accent_orange"]).pack(side="left", padx=(4, 0))
            else:
                tk.Label(laps_box, text="voltas", font=("Segoe UI", 9), bg=row["bg"], fg=C["text_muted"]).pack(side="left", padx=(4, 0))

            # Tag de Tipo de Pista
            tag_box = tk.Frame(row, bg=row["bg"])
            tag_box.pack(side="right", padx=(0, 20))

            if is_sprint:
                tag = tk.Label(tag_box, text="Sprint P2P", font=("Segoe UI", 8), bg="#3b2d18", fg=C["accent_orange"], padx=6, pady=1)
                tag.pack(side="left")
            else:
                tag = tk.Label(tag_box, text="Circuito", font=("Segoe UI", 8), bg=C["surface"], fg=C["accent_cyan"], padx=6, pady=1)
                tag.pack(side="left")

            self.track_items.append({
                "track_id": tid,
                "var_enabled": var_enabled,
                "var_laps": var_laps,
                "is_sprint": is_sprint,
            })

        self._update_track_counter()

    def _move_track_row(self, index, direction):
        target = index + direction
        if target < 0 or target >= len(self.track_items):
            return
        
        # Salva o estado atual na config temporária e reconstrói
        current_playlist = []
        for item in self.track_items:
            try:
                lval = int(item["var_laps"].get())
            except (ValueError, tk.TclError):
                lval = 3
            current_playlist.append({
                "track_id": item["track_id"],
                "enabled": item["var_enabled"].get(),
                "laps": lval,
            })

        # Swap
        current_playlist[index], current_playlist[target] = current_playlist[target], current_playlist[index]
        self.cfg["rotation_playlist"] = current_playlist
        self._populate_track_checklist()

    def _check_all_tracks(self):
        for item in self.track_items:
            item["var_enabled"].set(True)
        self._update_track_counter()

    def _uncheck_all_tracks(self):
        for item in self.track_items:
            item["var_enabled"].set(False)
        self._update_track_counter()

    def _set_all_laps(self, laps):
        val_str = str(laps)
        for item in self.track_items:
            if not item["is_sprint"] or laps == 1:
                item["var_laps"].set(val_str)

    def _apply_batch_laps(self):
        try:
            val = int(self.v_batch_laps.get())
        except (ValueError, tk.TclError):
            val = 3
        if val < 1:
            val = 1
        elif val > 99:
            val = 99
        self.v_batch_laps.set(str(val))
        self._set_all_laps(val)

    # -------------------------------------------------------------------------
    # ABA 2: POWER-UPS (EXATAMENTE COMO NO JOGO)
    # -------------------------------------------------------------------------
    def _init_tab_powerups(self):
        t = self.tab_powerups
        pw = self.cfg.get("powerup_options", {})

        self.v_pw_master = tk.BooleanVar(value=pw.get("master_enabled", True))
        self.v_pw_respawn = tk.StringVar(value=pw.get("respawn_rate", "Normal"))
        self.v_pw_random = tk.BooleanVar(value=pw.get("random_powerups", False))

        self.v_pw_nitro = tk.BooleanVar(value=pw.get("nitro", True))
        self.v_pw_barge = tk.BooleanVar(value=pw.get("barge", True))
        self.v_pw_shunt = tk.BooleanVar(value=pw.get("shunt", True))
        self.v_pw_bolt  = tk.BooleanVar(value=pw.get("bolt", True))
        self.v_pw_repair= tk.BooleanVar(value=pw.get("repair", True))
        self.v_pw_shield= tk.BooleanVar(value=pw.get("shield", True))
        self.v_pw_mine  = tk.BooleanVar(value=pw.get("mine", True))
        self.v_pw_shock = tk.BooleanVar(value=pw.get("shock", True))

        top_card = tk.Frame(t, bg=C["surface"], padx=14, pady=14, highlightthickness=1, highlightbackground=C["border"])
        top_card.pack(fill="x", pady=(0, 14))

        tk.Label(top_card, text="⚙️ Configurações Gerais de Power-ups", font=FONT_SECTION, bg=C["surface"], fg=C["accent_cyan"]).pack(anchor="w", pady=(0, 8))

        row1 = tk.Frame(top_card, bg=C["surface"])
        row1.pack(fill="x")

        tk.Checkbutton(row1, text="Power-up Options (Ativar Power-ups)", variable=self.v_pw_master,
                       bg=C["surface"], fg=C["text"], font=FONT_BOLD, selectcolor=C["surface2"],
                       activebackground=C["surface"], activeforeground=C["accent_cyan"]).pack(side="left", padx=(0, 24))

        tk.Label(row1, text="Power-up Respawn:", font=FONT_MAIN, bg=C["surface"], fg=C["text_muted"]).pack(side="left")
        cb_resp = ttk.Combobox(row1, values=["Normal", "Fast", "Slow", "Off"], textvariable=self.v_pw_respawn,
                               state="readonly", width=10, font=FONT_MAIN)
        cb_resp.pack(side="left", padx=(6, 24))

        tk.Checkbutton(row1, text="Random Power-ups (Itens Aleatórios)", variable=self.v_pw_random,
                       bg=C["surface"], fg=C["text"], font=FONT_MAIN, selectcolor=C["surface2"],
                       activebackground=C["surface"], activeforeground=C["accent_cyan"]).pack(side="left")

        grid_card = tk.Frame(t, bg=C["surface"], padx=14, pady=14, highlightthickness=1, highlightbackground=C["border"])
        grid_card.pack(fill="x")

        tk.Label(grid_card, text="🎮 Seleção Individual de Power-ups (Marque os permitidos na corrida):",
                 font=FONT_SECTION, bg=C["surface"], fg=C["text"]).pack(anchor="w", pady=(0, 12))

        pw_list = [
            ("Nitro",  "🚀 Aumento temporário extremo de velocidade",  self.v_pw_nitro,  C["pw_nitro"],  0, 0),
            ("Barge",  "💥 Onda de choque radial que empurra rivais", self.v_pw_barge,  C["pw_barge"],  0, 1),
            ("Shunt",  "🔴 Míssil teleguiado perseguidor",              self.v_pw_shunt,  C["pw_shunt"],  0, 2),
            ("Bolt",   "🌸 Três disparos retos de alta velocidade",    self.v_pw_bolt,   C["pw_bolt"],   1, 0),
            ("Repair", "🔧 Reparo imediato da blindagem do carro",     self.v_pw_repair, C["pw_repair"], 1, 1),
            ("Shield", "🛡️ Escudo protetor contra todos os ataques",   self.v_pw_shield, C["pw_shield"], 1, 2),
            ("Mine",   "🟠 Mina estática deixada na pista para trás",   self.v_pw_mine,   C["pw_mine"],   2, 0),
            ("Shock",  "⚡ Três campos elétricos na frente do 1º lugar", self.v_pw_shock,  C["pw_shock"],  2, 1),
        ]

        grid_frame = tk.Frame(grid_card, bg=C["surface"])
        grid_frame.pack(fill="x")

        for name, desc, var, col, r, c in pw_list:
            box = tk.Frame(grid_frame, bg=C["surface2"], padx=10, pady=8, highlightthickness=1, highlightbackground=col)
            box.grid(row=r, column=c, padx=6, pady=6, sticky="nsew")
            grid_frame.grid_columnconfigure(c, weight=1)

            cb = tk.Checkbutton(box, text=f"  {name}", variable=var, font=FONT_BOLD,
                                bg=C["surface2"], fg=col, selectcolor=C["surface"],
                                activebackground=C["surface2"], activeforeground=col)
            cb.pack(anchor="w")
            tk.Label(box, text=desc, font=("Segoe UI", 8), bg=C["surface2"], fg=C["text_muted"]).pack(anchor="w", padx=(20, 0))

        presets_bar = tk.Frame(grid_card, bg=C["surface"])
        presets_bar.pack(fill="x", pady=(14, 0))

        tk.Label(presets_bar, text="Atalhos Rápidos:", font=FONT_SMALL, bg=C["surface"], fg=C["text_muted"]).pack(side="left")
        tk.Button(presets_bar, text="✓ Marcar Todos", command=self._pw_select_all, bg=C["surface2"], fg=C["text"],
                  relief="flat", padx=10, pady=2, font=FONT_SMALL).pack(side="left", padx=4)
        tk.Button(presets_bar, text="✗ Desmarcar Todos", command=self._pw_deselect_all, bg=C["surface2"], fg=C["text_muted"],
                  relief="flat", padx=10, pady=2, font=FONT_SMALL).pack(side="left", padx=4)
        tk.Button(presets_bar, text="Apenas Shunts & Minas", command=self._pw_shunts_only, bg=C["surface2"], fg=C["accent_orange"],
                  relief="flat", padx=10, pady=2, font=FONT_SMALL).pack(side="left", padx=4)
        tk.Button(presets_bar, text="Apenas Nitros", command=self._pw_nitro_only, bg=C["surface2"], fg=C["green"],
                  relief="flat", padx=10, pady=2, font=FONT_SMALL).pack(side="left", padx=4)

    def _pw_select_all(self):
        for v in [self.v_pw_nitro, self.v_pw_barge, self.v_pw_shunt, self.v_pw_bolt, self.v_pw_repair, self.v_pw_shield, self.v_pw_mine, self.v_pw_shock]:
            v.set(True)

    def _pw_deselect_all(self):
        for v in [self.v_pw_nitro, self.v_pw_barge, self.v_pw_shunt, self.v_pw_bolt, self.v_pw_repair, self.v_pw_shield, self.v_pw_mine, self.v_pw_shock]:
            v.set(False)

    def _pw_shunts_only(self):
        self._pw_deselect_all()
        self.v_pw_shunt.set(True)
        self.v_pw_mine.set(True)

    def _pw_nitro_only(self):
        self._pw_deselect_all()
        self.v_pw_nitro.set(True)

    # -------------------------------------------------------------------------
    # ABA 3: OPÇÕES AVANÇADAS (ADVANCED OPTIONS)
    # -------------------------------------------------------------------------
    def _init_tab_advanced(self):
        t = self.tab_advanced
        adv = self.cfg.get("advanced_options", {})

        self.v_adv_damage   = tk.StringVar(value=adv.get("damage", "Medium"))
        self.v_adv_respawn  = tk.BooleanVar(value=adv.get("respawn", True))
        self.v_adv_handicap = tk.StringVar(value=adv.get("handicap", "High"))
        self.v_adv_timeout  = tk.BooleanVar(value=adv.get("timeout", True))
        self.v_adv_mods     = tk.BooleanVar(value=adv.get("mods", True))
        self.v_adv_upgrades = tk.BooleanVar(value=adv.get("upgrades", True))
        self.v_adv_ai       = tk.BooleanVar(value=adv.get("ai", False))

        card = tk.Frame(t, bg=C["surface"], padx=16, pady=16, highlightthickness=1, highlightbackground=C["border"])
        card.pack(fill="x")

        tk.Label(card, text="⚙️ Advanced Options (Opções de Regras da Sala)", font=FONT_SECTION, bg=C["surface"], fg=C["accent_cyan"]).pack(anchor="w", pady=(0, 14))

        grid = tk.Frame(card, bg=C["surface"])
        grid.pack(fill="x")

        # Damage
        f_dmg = tk.Frame(grid, bg=C["surface2"], padx=12, pady=10, highlightthickness=1, highlightbackground=C["border"])
        f_dmg.grid(row=0, column=0, padx=6, pady=6, sticky="nsew")
        tk.Label(f_dmg, text="💥 Damage (Dano nos Carros)", font=FONT_BOLD, bg=C["surface2"], fg=C["text"]).pack(anchor="w")
        cb_dmg = ttk.Combobox(f_dmg, values=["None", "Low", "Medium", "High", "Hardcore"],
                              textvariable=self.v_adv_damage, state="readonly", width=14, font=FONT_MAIN)
        cb_dmg.pack(anchor="w", pady=(4, 0))

        # Respawn
        f_resp = tk.Frame(grid, bg=C["surface2"], padx=12, pady=10, highlightthickness=1, highlightbackground=C["border"])
        f_resp.grid(row=0, column=1, padx=6, pady=6, sticky="nsew")
        tk.Label(f_resp, text="🔄 Respawn (Voltar à pista)", font=FONT_BOLD, bg=C["surface2"], fg=C["text"]).pack(anchor="w")
        tk.Checkbutton(f_resp, text="Ativado (On)", variable=self.v_adv_respawn, font=FONT_MAIN,
                       bg=C["surface2"], fg=C["accent_cyan"], selectcolor=C["surface"],
                       activebackground=C["surface2"], activeforeground=C["accent_cyan"]).pack(anchor="w", pady=(4, 0))

        # Handicap
        f_hnd = tk.Frame(grid, bg=C["surface2"], padx=12, pady=10, highlightthickness=1, highlightbackground=C["border"])
        f_hnd.grid(row=0, column=2, padx=6, pady=6, sticky="nsew")
        tk.Label(f_hnd, text="🚀 Handicap (Auxílio p/ retardatários)", font=FONT_BOLD, bg=C["surface2"], fg=C["text"]).pack(anchor="w")
        cb_hnd = ttk.Combobox(f_hnd, values=["None", "Low", "Medium", "High"],
                              textvariable=self.v_adv_handicap, state="readonly", width=14, font=FONT_MAIN)
        cb_hnd.pack(anchor="w", pady=(4, 0))

        # Timeout
        f_tm = tk.Frame(grid, bg=C["surface2"], padx=12, pady=10, highlightthickness=1, highlightbackground=C["border"])
        f_tm.grid(row=1, column=0, padx=6, pady=6, sticky="nsew")
        tk.Label(f_tm, text="⏱️ Timeout (Tempo limite final)", font=FONT_BOLD, bg=C["surface2"], fg=C["text"]).pack(anchor="w")
        tk.Checkbutton(f_tm, text="Ativado (On)", variable=self.v_adv_timeout, font=FONT_MAIN,
                       bg=C["surface2"], fg=C["accent_cyan"], selectcolor=C["surface"],
                       activebackground=C["surface2"], activeforeground=C["accent_cyan"]).pack(anchor="w", pady=(4, 0))

        # Mods
        f_mod = tk.Frame(grid, bg=C["surface2"], padx=12, pady=10, highlightthickness=1, highlightbackground=C["border"])
        f_mod.grid(row=1, column=1, padx=6, pady=6, sticky="nsew")
        tk.Label(f_mod, text="🔧 Mods (Perks dos carros)", font=FONT_BOLD, bg=C["surface2"], fg=C["text"]).pack(anchor="w")
        tk.Checkbutton(f_mod, text="Ativado (On)", variable=self.v_adv_mods, font=FONT_MAIN,
                       bg=C["surface2"], fg=C["accent_cyan"], selectcolor=C["surface"],
                       activebackground=C["surface2"], activeforeground=C["accent_cyan"]).pack(anchor="w", pady=(4, 0))

        # Upgrades
        f_upg = tk.Frame(grid, bg=C["surface2"], padx=12, pady=10, highlightthickness=1, highlightbackground=C["border"])
        f_upg.grid(row=1, column=2, padx=6, pady=6, sticky="nsew")
        tk.Label(f_upg, text="💡 Upgrades (Melhorias)", font=FONT_BOLD, bg=C["surface2"], fg=C["text"]).pack(anchor="w")
        tk.Checkbutton(f_upg, text="Ativado (On)", variable=self.v_adv_upgrades, font=FONT_MAIN,
                       bg=C["surface2"], fg=C["accent_cyan"], selectcolor=C["surface"],
                       activebackground=C["surface2"], activeforeground=C["accent_cyan"]).pack(anchor="w", pady=(4, 0))

        # AI
        f_ai = tk.Frame(grid, bg=C["surface2"], padx=12, pady=10, highlightthickness=1, highlightbackground=C["border"])
        f_ai.grid(row=2, column=0, padx=6, pady=6, sticky="nsew")
        tk.Label(f_ai, text="🤖 AI (Bots na sala)", font=FONT_BOLD, bg=C["surface2"], fg=C["text"]).pack(anchor="w")
        tk.Checkbutton(f_ai, text="Preencher com Bots (On)", variable=self.v_adv_ai, font=FONT_MAIN,
                       bg=C["surface2"], fg=C["accent_pink"], selectcolor=C["surface"],
                       activebackground=C["surface2"], activeforeground=C["accent_pink"]).pack(anchor="w", pady=(4, 0))

        grid.grid_columnconfigure(0, weight=1)
        grid.grid_columnconfigure(1, weight=1)
        grid.grid_columnconfigure(2, weight=1)

    # -------------------------------------------------------------------------
    # ABA 4: BoP & MULTI-CLASS
    # -------------------------------------------------------------------------
    def _init_tab_bop(self):
        t = self.tab_bop
        gp = self.cfg.get("gameplay", {})

        self.v_bop = tk.BooleanVar(value=gp.get("bop_enabled", True))
        self.v_unlock_classes = tk.BooleanVar(value=gp.get("all_classes_unlocked", True))
        self.v_bop_d = tk.DoubleVar(value=gp.get("bop_class_d_multiplier", 1.48))
        self.v_bop_c = tk.DoubleVar(value=gp.get("bop_class_c_multiplier", 1.28))
        self.v_bop_b = tk.DoubleVar(value=gp.get("bop_class_b_multiplier", 1.14))

        card = tk.Frame(t, bg=C["surface"], padx=16, pady=14, highlightthickness=1, highlightbackground=C["border"])
        card.pack(fill="x")

        tk.Label(card, text="🏎️ Fusca x Astra — BoP (Balance of Performance Proporcional)", font=FONT_SECTION, bg=C["surface"], fg=C["accent_orange"]).pack(anchor="w")
        tk.Label(card, text="Equipara carros de classes menores ao ritmo da Classe A, preservando o peso, aderência e estilo de cada veículo.",
                 font=FONT_SMALL, bg=C["surface"], fg=C["text_muted"]).pack(anchor="w", pady=(2, 8))

        row_cbs = tk.Frame(card, bg=C["surface"])
        row_cbs.pack(fill="x", pady=(0, 10))

        tk.Checkbutton(row_cbs, text="Ativar Balance of Performance (Equiparar todas as classes à Classe A)",
                       variable=self.v_bop, bg=C["surface"], fg=C["text"],
                       selectcolor=C["surface2"], activebackground=C["surface"],
                       activeforeground=C["accent_cyan"], font=FONT_BOLD).pack(side="left")

        tk.Checkbutton(row_cbs, text="Desbloquear Garagem Completa (Misturar D, C, B e A na mesma sala)",
                       variable=self.v_unlock_classes, bg=C["surface"], fg=C["text"],
                       selectcolor=C["surface2"], activebackground=C["surface"],
                       activeforeground=C["accent_cyan"], font=FONT_BOLD).pack(side="left", padx=(20, 0))

        # Nota explicativa
        note_box = tk.Frame(card, bg=C["surface2"], padx=10, pady=6, highlightthickness=1, highlightbackground=C["border"])
        note_box.pack(fill="x", pady=(0, 10))
        tk.Label(note_box, text="💡 Como funciona o BoP real: Como D < C < B < A, cada classe recebe um fator proporcional diferente para que todos atinjam a velocidade da Classe A (~185-195 mph). Assim, a Classe B não fica apelona e o Fusca (D) consegue disputar com o Astra (A).",
                 font=("Segoe UI Italic", 8), bg=C["surface2"], fg=C["accent_cyan"], wraplength=760, justify="left").pack(anchor="w")

        # Sliders por Classe
        sliders_frame = tk.Frame(card, bg=C["surface"])
        sliders_frame.pack(fill="x", pady=4)

        # Classe D
        row_d = tk.Frame(sliders_frame, bg=C["surface"])
        row_d.pack(fill="x", pady=4)
        tk.Label(row_d, text="🚗 Classe D (Fusca, Beetle, etc.):", font=FONT_MAIN, bg=C["surface"], fg=C["text"], width=32, anchor="w").pack(side="left")
        tk.Scale(row_d, from_=1.0, to=1.80, resolution=0.02, orient="horizontal", variable=self.v_bop_d,
                 bg=C["surface"], fg=C["text"], highlightthickness=0, troughcolor=C["surface2"], length=220).pack(side="left", padx=10)
        tk.Label(row_d, text="Boost: +48% (125mph -> ~185mph)", font=FONT_SMALL, bg=C["surface"], fg=C["accent_orange"]).pack(side="left")

        # Classe C
        row_c = tk.Frame(sliders_frame, bg=C["surface"])
        row_c.pack(fill="x", pady=4)
        tk.Label(row_c, text="🚙 Classe C (Land Rover, Golf, Focus):", font=FONT_MAIN, bg=C["surface"], fg=C["text"], width=32, anchor="w").pack(side="left")
        tk.Scale(row_c, from_=1.0, to=1.60, resolution=0.02, orient="horizontal", variable=self.v_bop_c,
                 bg=C["surface"], fg=C["text"], highlightthickness=0, troughcolor=C["surface2"], length=220).pack(side="left", padx=10)
        tk.Label(row_c, text="Boost: +28% (145mph -> ~185mph)", font=FONT_SMALL, bg=C["surface"], fg=C["accent_cyan"]).pack(side="left")

        # Classe B
        row_b = tk.Frame(sliders_frame, bg=C["surface"])
        row_b.pack(fill="x", pady=4)
        tk.Label(row_b, text="🏎️ Classe B (BMW M3, Audi TTS, 350Z):", font=FONT_MAIN, bg=C["surface"], fg=C["text"], width=32, anchor="w").pack(side="left")
        tk.Scale(row_b, from_=1.0, to=1.40, resolution=0.02, orient="horizontal", variable=self.v_bop_b,
                 bg=C["surface"], fg=C["text"], highlightthickness=0, troughcolor=C["surface2"], length=220).pack(side="left", padx=10)
        tk.Label(row_b, text="Boost: +14% (165mph -> ~185mph)", font=FONT_SMALL, bg=C["surface"], fg=C["green"]).pack(side="left")

        # Classe A
        row_a = tk.Frame(sliders_frame, bg=C["surface"])
        row_a.pack(fill="x", pady=4)
        tk.Label(row_a, text="🏁 Classe A (Astra, Corvette, Viper):", font=FONT_MAIN, bg=C["surface"], fg=C["text_muted"], width=32, anchor="w").pack(side="left")
        tk.Label(row_a, text="1.00x (Carro de Referência Oficial - Sem alteração)", font=FONT_BOLD, bg=C["surface"], fg=C["text_muted"]).pack(side="left", padx=10)

        # Botão Restaurar Padrões
        btn_bar = tk.Frame(card, bg=C["surface"])
        btn_bar.pack(fill="x", pady=(10, 0))
        tk.Button(btn_bar, text="↺ Restaurar Proporções Ideais (FIA GT3 BoP)", command=self._reset_bop_defaults,
                  bg=C["surface2"], fg=C["accent_cyan"], relief="flat", padx=10, pady=3, font=FONT_SMALL).pack(side="left")

    def _reset_bop_defaults(self):
        self.v_bop_d.set(1.48)
        self.v_bop_c.set(1.28)
        self.v_bop_b.set(1.14)

    # -------------------------------------------------------------------------
    # ABA 5: REDE & LAN
    # -------------------------------------------------------------------------
    def _init_tab_network(self):
        t = self.tab_network
        net = self.cfg.get("network", {})

        self.v_bind_ip = tk.StringVar(value=net.get("bind_ip", "auto"))
        self.v_target_ips = tk.StringVar(value=net.get("target_ips", "10.1.1.31, 10.1.1.88"))

        card = tk.Frame(t, bg=C["surface"], padx=16, pady=16, highlightthickness=1, highlightbackground=C["border"])
        card.pack(fill="x")

        tk.Label(card, text="🌐 Configurações de Conexão LAN e Firewall", font=FONT_SECTION, bg=C["surface"], fg=C["accent_cyan"]).pack(anchor="w")
        tk.Label(card, text="Bypass inteligente de Firewalls corporativos (Fortinet) e roteamento de adaptadores.",
                 font=FONT_SMALL, bg=C["surface"], fg=C["text_muted"]).pack(anchor="w", pady=(2, 12))

        tk.Label(card, text="BindIP (IP da placa de rede local deste computador):", font=FONT_MAIN, bg=C["surface"], fg=C["text"]).pack(anchor="w")
        tk.Label(card, text="Use 'auto' para autodetectar a placa física com internet, ou insira o IP manual (ex: 10.1.1.31):",
                 font=FONT_SMALL, bg=C["surface"], fg=C["text_muted"]).pack(anchor="w")
        tk.Entry(card, textvariable=self.v_bind_ip, bg=C["surface2"], fg=C["text"], font=FONT_MAIN, width=30,
                 relief="flat", highlightthickness=1, highlightbackground=C["border"]).pack(anchor="w", pady=(4, 14))

        tk.Label(card, text="TargetIPs (Lista de IPs de todos os jogadores para Unicast):", font=FONT_MAIN, bg=C["surface"], fg=C["text"]).pack(anchor="w")
        tk.Label(card, text="Separe por vírgula. Coloque o seu próprio IP e o dos outros computadores:",
                 font=FONT_SMALL, bg=C["surface"], fg=C["text_muted"]).pack(anchor="w")
        tk.Entry(card, textvariable=self.v_target_ips, bg=C["surface2"], fg=C["text"], font=FONT_MAIN, width=55,
                 relief="flat", highlightthickness=1, highlightbackground=C["border"]).pack(anchor="w", pady=(4, 6))

    # -------------------------------------------------------------------------
    # ABA 6: COMBATE & DISCORD
    # -------------------------------------------------------------------------
    def _init_tab_combat(self):
        t = self.tab_combat
        comb = self.cfg.get("combat_telemetry", {})
        disc = self.cfg.get("discord", {})

        self.v_comb_enabled = tk.BooleanVar(value=comb.get("enabled", True))
        self.v_comb_db      = tk.BooleanVar(value=comb.get("save_to_database", True))
        self.v_disc_enabled = tk.BooleanVar(value=disc.get("webhook_enabled", False))
        self.v_disc_url     = tk.StringVar(value=disc.get("webhook_url", ""))

        card_comb = tk.Frame(t, bg=C["surface"], padx=16, pady=16, highlightthickness=1, highlightbackground=C["border"])
        card_comb.pack(fill="x", pady=(0, 14))

        tk.Label(card_comb, text="🎯 Telemetria de Combate (Quem atirou em quem)", font=FONT_SECTION, bg=C["surface"], fg=C["accent_cyan"]).pack(anchor="w")
        tk.Label(card_comb, text="Captura em tempo real todos os disparos, acertos e defesas da corrida.",
                 font=FONT_SMALL, bg=C["surface"], fg=C["text_muted"]).pack(anchor="w", pady=(2, 10))

        tk.Checkbutton(card_comb, text="Gravar estatísticas de combate (Atacante -> Vítima -> Power-up)",
                       variable=self.v_comb_enabled, bg=C["surface"], fg=C["text"],
                       selectcolor=C["surface2"], activebackground=C["surface"],
                       activeforeground=C["accent_cyan"], font=FONT_MAIN).pack(anchor="w")

        tk.Checkbutton(card_comb, text="Salvar histórico no banco de dados local SQLite (Rankings e Rivalidades)",
                       variable=self.v_comb_db, bg=C["surface"], fg=C["text"],
                       selectcolor=C["surface2"], activebackground=C["surface"],
                       activeforeground=C["accent_cyan"], font=FONT_MAIN).pack(anchor="w", pady=(4, 0))

        card_disc = tk.Frame(t, bg=C["surface"], padx=16, pady=16, highlightthickness=1, highlightbackground=C["border"])
        card_disc.pack(fill="x")

        tk.Label(card_disc, text="🤖 Notificações no Discord (Webhook)", font=FONT_SECTION, bg=C["surface"], fg="#7289da").pack(anchor="w")
        tk.Label(card_disc, text="Envia automaticamente o pódio, MVP e estatísticas da corrida para o canal do Discord.",
                 font=FONT_SMALL, bg=C["surface"], fg=C["text_muted"]).pack(anchor="w", pady=(2, 10))

        tk.Checkbutton(card_disc, text="Ativar postagem automática no Discord",
                       variable=self.v_disc_enabled, bg=C["surface"], fg=C["text"],
                       selectcolor=C["surface2"], activebackground=C["surface"],
                       activeforeground=C["accent_cyan"], font=FONT_MAIN).pack(anchor="w")

        tk.Label(card_disc, text="Discord Webhook URL:", font=FONT_MAIN, bg=C["surface"], fg=C["text"]).pack(anchor="w", pady=(8, 2))
        tk.Entry(card_disc, textvariable=self.v_disc_url, bg=C["surface2"], fg=C["text"], font=FONT_MAIN, width=65,
                 relief="flat", highlightthickness=1, highlightbackground=C["border"]).pack(anchor="w", pady=(0, 6))

    # -------------------------------------------------------------------------
    # RODAPÉ
    # -------------------------------------------------------------------------
    def _build_footer(self):
        footer = tk.Frame(self, bg=C["bg"], pady=12, padx=16)
        footer.pack(fill="x", side="bottom")

        self.lbl_status = tk.Label(footer, text="Pronto para configurar.", font=FONT_SMALL, bg=C["bg"], fg=C["text_muted"])
        self.lbl_status.pack(side="left")

        btn_save = tk.Button(footer, text="💾 Salvar Configurações", command=self._save, bg=C["green"], fg="#ffffff",
                             font=("Segoe UI Bold", 10), activebackground="#059669", relief="flat", padx=18, pady=6)
        btn_save.pack(side="right", padx=(8, 0))

    def _save(self):
        playlist_items = []
        for item in self.track_items:
            try:
                lval = int(item["var_laps"].get())
            except (ValueError, tk.TclError):
                lval = 3
            if lval < 1:
                lval = 1
            elif lval > 99:
                lval = 99

            playlist_items.append({
                "track_id": item["track_id"],
                "enabled": item["var_enabled"].get(),
                "laps": lval,
            })

        try:
            def_laps_val = int(self.v_def_laps.get())
        except (ValueError, tk.TclError):
            def_laps_val = 3

        cfg_to_save = {
            "server": {
                "auto_rotation_enabled": self.v_auto_rot.get(),
                "rotation_mode": self.v_rot_mode.get(),
                "countdown_seconds": self.v_countdown.get(),
                "auto_start_enabled": self.v_auto_start.get(),
                "default_laps": def_laps_val,
                "anti_afk_enabled": self.cfg.get("server", {}).get("anti_afk_enabled", True),
                "anti_afk_timeout_seconds": self.cfg.get("server", {}).get("anti_afk_timeout_seconds", 30),
            },
            "powerup_options": {
                "master_enabled": self.v_pw_master.get(),
                "respawn_rate": self.v_pw_respawn.get(),
                "random_powerups": self.v_pw_random.get(),
                "nitro": self.v_pw_nitro.get(),
                "barge": self.v_pw_barge.get(),
                "shunt": self.v_pw_shunt.get(),
                "bolt": self.v_pw_bolt.get(),
                "repair": self.v_pw_repair.get(),
                "shield": self.v_pw_shield.get(),
                "mine": self.v_pw_mine.get(),
                "shock": self.v_pw_shock.get(),
            },
            "advanced_options": {
                "damage": self.v_adv_damage.get(),
                "respawn": self.v_adv_respawn.get(),
                "handicap": self.v_adv_handicap.get(),
                "timeout": self.v_adv_timeout.get(),
                "mods": self.v_adv_mods.get(),
                "upgrades": self.v_adv_upgrades.get(),
                "ai": self.v_adv_ai.get(),
            },
            "gameplay": {
                "bop_enabled": self.v_bop.get(),
                "bop_target_class": "A",
                "bop_class_d_multiplier": round(self.v_bop_d.get(), 2),
                "bop_class_c_multiplier": round(self.v_bop_c.get(), 2),
                "bop_class_b_multiplier": round(self.v_bop_b.get(), 2),
                "all_classes_unlocked": self.v_unlock_classes.get(),
            },
            "network": {
                "bind_ip": self.v_bind_ip.get().strip(),
                "target_ips": self.v_target_ips.get().strip(),
            },
            "combat_telemetry": {
                "enabled": self.v_comb_enabled.get(),
                "log_hits": True,
                "save_to_database": self.v_comb_db.get(),
            },
            "discord": {
                "webhook_enabled": self.v_disc_enabled.get(),
                "webhook_url": self.v_disc_url.get().strip(),
            },
            "rotation_playlist": playlist_items,
        }

        try:
            save_config(cfg_to_save)
            self.lbl_status.config(text=f"✓ Configurações salvas em {CONFIG_PATH.name}!", fg=C["green"])
            messagebox.showinfo("Sucesso", f"Configurações gravadas com sucesso em:\n{CONFIG_PATH}")
        except Exception as e:
            self.lbl_status.config(text=f"Erro ao salvar: {e}", fg=C["red"])
            messagebox.showerror("Erro ao salvar", str(e))


def main():
    app = BlurMTXControlApp()
    app.mainloop()


if __name__ == "__main__":
    main()
