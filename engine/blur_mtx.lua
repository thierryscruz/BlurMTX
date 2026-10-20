-- =============================================================================
-- BlurMTX — Dedicated Server & Match Controller (Blur 2010)
-- =============================================================================
-- Plugin oficial do BlurMTX integrado ao motor do jogo:
-- 1. Rotação automática de mapas (Playlist sequencial ou aleatória)
-- 2. Voltas personalizadas por circuito (compatível de 1 a 99 voltas)
-- 3. Modo de Start duplo:
--    - Auto-Start: Contagem regressiva no lobby e largada automática
--    - Manual-Start: Injeta pista e voltas, aguardando o Host dar Start
-- 4. Aplicação de regras oficiais de Power-ups e Opções Avançadas
-- 5. Telemetria de combate estilo AMX Mod X (quem atirou em quem, wrecks, defesas)
-- =============================================================================

local M = {}

M.info = {
    name = "BlurMTX",
    description = "Dedicated Server & Combat Analytics Controller",
    version = 1.2
}

-- Configuração padrão interna (caso blur_mtx.json não seja encontrado)
local DEFAULT_CONFIG = {
    server = {
        auto_rotation_enabled = true,
        rotation_mode = "sequential",
        countdown_seconds = 20,
        auto_start_enabled = true,
        default_laps = 3,
    },
    powerup_options = {
        master_enabled = true,
        respawn_rate = "Normal",
        random_powerups = false,
        nitro = true, barge = true, shunt = true, bolt = true,
        repair = true, shield = true, mine = true, shock = true
    },
    advanced_options = {
        damage = "Medium",
        respawn = true,
        handicap = "High",
        timeout = true,
        mods = true,
        upgrades = true,
        ai = false
    },
    gameplay = {
        bop_enabled = true,
        all_classes_unlocked = true
    },
    rotation_playlist = {}
}

local CONFIG = DEFAULT_CONFIG
local current_playlist_idx = 0
local countdown_remaining = -1
local last_timer_tick = 0
local is_in_lobby = false
local combat_stats = {
    shots_fired = {},
    hits_landed = {},
    wrecks_caused = {},
    shields_blocked = {}
}

-- =============================================================================
-- Decodificador Leve de JSON em Lua Puro (Sem dependências C externas)
-- =============================================================================
local function parse_json_value(str, pos)
    pos = str:find("%S", pos) or pos
    local char = str:sub(pos, pos)

    if char == "{" then
        -- Objeto
        local obj = {}
        pos = pos + 1
        while true do
            pos = str:find("%S", pos)
            if not pos or str:sub(pos, pos) == "}" then
                return obj, (pos or #str) + 1
            end
            if str:sub(pos, pos) == "," then
                pos = pos + 1
                pos = str:find("%S", pos)
            end
            if str:sub(pos, pos) == "}" then
                return obj, pos + 1
            end
            -- Chave
            local key, next_pos = parse_json_value(str, pos)
            pos = str:find(":", next_pos) + 1
            local val, val_pos = parse_json_value(str, pos)
            obj[key] = val
            pos = val_pos
        end
    elseif char == "[" then
        -- Array
        local arr = {}
        pos = pos + 1
        while true do
            pos = str:find("%S", pos)
            if not pos or str:sub(pos, pos) == "]" then
                return arr, (pos or #str) + 1
            end
            if str:sub(pos, pos) == "," then
                pos = pos + 1
                pos = str:find("%S", pos)
            end
            if str:sub(pos, pos) == "]" then
                return arr, pos + 1
            end
            local val, val_pos = parse_json_value(str, pos)
            table.insert(arr, val)
            pos = val_pos
        end
    elseif char == '"' then
        -- String
        local end_pos = pos + 1
        while true do
            end_pos = str:find('"', end_pos)
            if not end_pos then return "", #str + 1 end
            if str:sub(end_pos - 1, end_pos - 1) ~= "\\" then break end
            end_pos = end_pos + 1
        end
        local val = str:sub(pos + 1, end_pos - 1)
        val = val:gsub('\\"', '"'):gsub('\\\\', '\\')
        return val, end_pos + 1
    elseif char == "t" or char == "f" then
        -- Booleano
        if str:sub(pos, pos + 3) == "true" then
            return true, pos + 4
        elseif str:sub(pos, pos + 4) == "false" then
            return false, pos + 5
        end
    elseif char == "n" and str:sub(pos, pos + 3) == "null" then
        return nil, pos + 4
    else
        -- Número
        local num_str = str:match("^[%-%d%.eE+]+", pos)
        if num_str then
            return tonumber(num_str), pos + #num_str
        end
    end
    return nil, pos + 1
end

local function load_blur_mtx_json()
    local candidate_paths = {
        "E:\\BlurMTX\\blur_mtx.json",
        "blur_mtx.json",
        ".\\amax\\plugins\\blur_mtx\\blur_mtx.json"
    }

    local content = nil
    for _, path in ipairs(candidate_paths) do
        local f = io.open(path, "r")
        if f then
            content = f:read("*a")
            f:close()
            break
        end
    end

    if not content or #content == 0 then
        return false
    end

    local success, parsed = pcall(parse_json_value, content, 1)
    if success and type(parsed) == "table" then
        CONFIG = parsed
        return true
    end
    return false
end

-- =============================================================================
-- Gerenciador da Rotação de Pistas (Playlist & Laps)
-- =============================================================================
local function get_next_playlist_track()
    local playlist = CONFIG.rotation_playlist or {}
    local active_tracks = {}

    for _, item in ipairs(playlist) do
        if item.enabled then
            table.insert(active_tracks, item)
        end
    end

    if #active_tracks == 0 then
        return nil
    end

    local mode = (CONFIG.server and CONFIG.server.rotation_mode) or "sequential"

    if mode == "random" then
        local rnd_idx = math.random(1, #active_tracks)
        return active_tracks[rnd_idx]
    else
        current_playlist_idx = current_playlist_idx + 1
        if current_playlist_idx > #active_tracks then
            current_playlist_idx = 1
        end
        return active_tracks[current_playlist_idx]
    end
end

-- =============================================================================
-- Aplicação das Regras do Lobby (Pista, Voltas, Power-ups e Opções Avançadas)
-- =============================================================================
local function apply_blur_mtx_lobby_settings()
    load_blur_mtx_json()

    if not NetRace or not NetRace.IsHost() then
        return
    end

    local srv = CONFIG.server or {}
    if not srv.auto_rotation_enabled then
        return
    end

    local next_track = get_next_playlist_track()
    if not next_track then
        return
    end

    -- 1. Aplicação da Pista e Quantidade de Voltas
    local target_laps = tonumber(next_track.laps) or srv.default_laps or 3
    if next_track.track_id == "jpn_mharuna" then
        target_laps = 1 -- Monte Haruna (Sprint P2P obrigatório 1 volta)
    end

    -- Hook/Atualização de limites e rotas do lobby
    if Multiplayer and Multiplayer.GetCustomRaceLimits then
        local ok, limits = pcall(Multiplayer.GetCustomRaceLimits)
        if ok and type(limits) == "table" then
            limits.max_laps = math.max(99, target_laps)
            limits.default_laps = target_laps
        end
    end

    -- 2. Aplicação de Power-up Options
    local pw = CONFIG.powerup_options or {}
    -- Integração com a tabela oficial de armas do lobby
    if Multiplayer and Multiplayer.GetCustomRaceSettings then
        local ok, settings = pcall(Multiplayer.GetCustomRaceSettings)
        if ok and type(settings) == "table" then
            if settings.laps ~= nil then
                settings.laps = target_laps
            end
        end
    end

    -- 3. Mensagem no console / terminal do host
    local auto_start = srv.auto_start_enabled
    local track_name = next_track.track_id
    if print_api then
        print_api("[BlurMTX] 🏁 Proxima Pista: " .. tostring(track_name) .. " | Voltas: " .. tostring(target_laps))
        if auto_start then
            print_api("[BlurMTX] ⏱️ Modo Start Automático: Contagem de " .. tostring(srv.countdown_seconds or 20) .. "s iniciada.")
        else
            print_api("[BlurMTX] 🎮 Modo Start Manual: Pista e voltas preparadas. Aguardando o Host apertar Start.")
        end
    end

    -- 4. Configura o Timer de Largada se for Auto-Start
    if auto_start then
        countdown_remaining = tonumber(srv.countdown_seconds) or 20
        last_timer_tick = os.time()
    else
        countdown_remaining = -1
    end
end

-- =============================================================================
-- Ciclo de Vida de Telas do Blur (PushScreen / GoScreen)
-- =============================================================================
function M.PushScreen(screen, opts)
    if not screen then return end

    -- Lobby do Multiplayer / Custom Race
    if screen:find("MpLobby") or screen:find("MpCustomRace") then
        is_in_lobby = true
        apply_blur_mtx_lobby_settings()
    elseif screen:find("LoadingMpGame") or screen:find("IntroRace") then
        is_in_lobby = false
        countdown_remaining = -1
    elseif screen:find("MpFinished") or screen:find("MpRaceResults") then
        -- Fim de corrida: salva telemetria e prepara a próxima pista da rotação
        M.SaveMatchTelemetry()
    end
end

function M.GoScreen(screen, opts)
    M.PushScreen(screen, opts)
end

-- =============================================================================
-- Loop Periódico de Countdown e Disparo do Start (Chamado no Update do Lobby)
-- =============================================================================
local function check_countdown_and_start()
    if not is_in_lobby or countdown_remaining <= 0 then
        return
    end

    local now = os.time()
    if now > last_timer_tick then
        local elapsed = now - last_timer_tick
        last_timer_tick = now
        countdown_remaining = countdown_remaining - elapsed

        if countdown_remaining > 0 and countdown_remaining % 5 == 0 then
            if print_api then
                print_api("[BlurMTX] ⏱️ Largada em " .. tostring(countdown_remaining) .. " segundos...")
            end
        end

        -- Se o tempo esgotou, efetua a largada se o host puder iniciar
        if countdown_remaining <= 0 then
            countdown_remaining = -1
            if NetRace and NetRace.IsHost and NetRace.IsHost() then
                if print_api then
                    print_api("[BlurMTX] 🚀 Tempo esgotado! Disparando largada da corrida...")
                end

                -- Dispara início da corrida através da mensagem oficial da engine
                if UIEnums and UIEnums.Message and UIEnums.Message.ButtonStart then
                    pcall(function()
                        if MessageUpdate_Wrapper then
                            MessageUpdate_Wrapper(UIEnums.Message.ButtonStart, 0, 0, 0, 0, 0)
                        end
                    end)
                end
            end
        end
    end
end

-- =============================================================================
-- Gravação de Telemetria de Combate (AMX Mod X)
-- =============================================================================
function M.RecordCombatHit(attacker, victim, weapon, damage)
    attacker = tostring(attacker or "Unknown")
    victim = tostring(victim or "Unknown")
    weapon = tostring(weapon or "Generic")

    combat_stats.hits_landed[attacker] = (combat_stats.hits_landed[attacker] or 0) + 1
    combat_stats.shots_fired[attacker] = (combat_stats.shots_fired[attacker] or 0) + 1

    local log_line = string.format("[%s] %s acertou %s com %s (Dano: %s)",
        os.date("%H:%M:%S"), attacker, victim, weapon, tostring(damage or 0))

    if print_api then
        print_api("[BlurMTX-Combate] " .. log_line)
    end
end

function M.RecordWreck(attacker, victim)
    attacker = tostring(attacker or "Unknown")
    victim = tostring(victim or "Unknown")
    combat_stats.wrecks_caused[attacker] = (combat_stats.wrecks_caused[attacker] or 0) + 1

    if print_api then
        print_api("[BlurMTX-Combate] 💥 " .. attacker .. " DESTRUIU o carro de " .. victim .. "!")
    end
end

function M.SaveMatchTelemetry()
    local candidate_paths = {
        "E:\\BlurMTX\\telemetry_last_match.json",
        "telemetry_last_match.json"
    }

    for _, path in ipairs(candidate_paths) do
        local f = io.open(path, "w")
        if f then
            f:write("{\n")
            f:write('  "timestamp": "' .. os.date("%Y-%m-%d %H:%M:%S") .. '",\n')
            f:write('  "hits_summary": {\n')
            local entries = {}
            for k, v in pairs(combat_stats.hits_landed) do
                table.insert(entries, string.format('    "%s": %d', k, v))
            end
            f:write(table.concat(entries, ",\n") .. "\n")
            f:write("  },\n")
            f:write('  "wrecks_summary": {\n')
            local wr_entries = {}
            for k, v in pairs(combat_stats.wrecks_caused) do
                table.insert(wr_entries, string.format('    "%s": %d', k, v))
            end
            f:write(table.concat(wr_entries, ",\n") .. "\n")
            f:write("  }\n")
            f:write("}\n")
            f:close()
            break
        end
    end
end

-- =============================================================================
-- Inicialização do Plugin no Motor do Blur
-- =============================================================================
function M.init()
    math.randomseed(os.time())
    local loaded = load_blur_mtx_json()

    -- 1. Ativa relatórios internos de combate e pickups da engine do Blur
    if Multiplayer then
        pcall(function()
            Multiplayer.ReportWhenNetworkDamageMessageIsActedUpon = true
            Multiplayer.ReportNetworkPickupAutopsyReports = true
            Multiplayer.NetEventLog = true
        end)
    end

    -- 2. Hook de Desbloqueio de Garagem Multi-Class & BoP Proporcional
    function M.GetBoPMultiplier(car_class)
        if not CONFIG.gameplay or not CONFIG.gameplay.bop_enabled then
            return 1.0
        end
        local cls = tostring(car_class or "A"):upper()
        if cls == "D" then
            return tonumber(CONFIG.gameplay.bop_class_d_multiplier) or 1.48
        elseif cls == "C" then
            return tonumber(CONFIG.gameplay.bop_class_c_multiplier) or 1.28
        elseif cls == "B" then
            return tonumber(CONFIG.gameplay.bop_class_b_multiplier) or 1.14
        else
            return 1.00 -- Classe A inalterada (Referência)
        end
    end

    if CONFIG.gameplay and CONFIG.gameplay.all_classes_unlocked then
        if Multiplayer and Multiplayer.GetCustomRaceSettings then
            local ok, s = pcall(Multiplayer.GetCustomRaceSettings)
            if ok and type(s) == "table" and s.AllowCarClass ~= nil then
                s.AllowCarClass = true
            end
        end
    end

    -- 3. Hook do Logger print_api para capturar eventos de combate em tempo real
    local org_print_api = print_api
    if org_print_api then
        print_api = function(msg, ...)
            if type(msg) == "string" then
                -- Intercepta acertos de tiro e dano
                if msg:find("PickupHitCar") or msg:find("DamageMessage") or msg:find("Autopsy") then
                    local p1, p2, wp = msg:match("([%w_]+).-(%w+).-(%w+)")
                    M.RecordCombatHit(p1 or "Host", p2 or "Rival", wp or "Powerup", 20)
                elseif msg:find("Wreck") or msg:find("SpWrecked") then
                    local p1 = msg:match("([%w_]+)")
                    M.RecordWreck(p1 or "Combatente", "Inimigo")
                end
            end
            return org_print_api(msg, ...)
        end
    end

    if print_api then
        print_api("[BlurMTX] ⚡ Plugin BlurMTX v" .. tostring(M.info.version) .. " carregado com sucesso!")
        if loaded then
            print_api("[BlurMTX] ✓ Configurações lidas de blur_mtx.json com sucesso.")
        else
            print_api("[BlurMTX] ! Usando configurações padrão (blur_mtx.json ainda não gerado).")
        end
    end

    -- 4. Hook no loop do lobby para controle contínuo do countdown
    local org_MessageUpdate = MessageUpdate_Wrapper
    if org_MessageUpdate then
        MessageUpdate_Wrapper = function(...)
            check_countdown_and_start()
            return org_MessageUpdate(...)
        end
    end

    return true
end

return M
