@echo off
setlocal EnableDelayedExpansion
title BlurMTX - Iniciar Servidor Completo
color 0b

echo =====================================================================
echo   ⚡ BlurMTX - Iniciando Servidor Dedicado e Servicos
echo =====================================================================
echo.

set "BASE_DIR=%~dp0"
cd /d "!BASE_DIR!"

echo [1/4] Verificando instalacao do plugin no jogo...
if not exist "E:\Blur(tm)\amax\plugins\blur_mtx\blur_mtx.lua" (
    echo  -> Plugin nao encontrado no jogo. Instalando agora...
    call "!BASE_DIR!instalar_no_jogo.bat"
) else (
    echo  -> Plugin BlurMTX ja esta instalado no jogo.
)

echo [2/4] Iniciando Web Dashboard na porta 8080...
start "BlurMTX - Web Dashboard" cmd /c "python web/app.py"

echo [3/4] Iniciando Orquestrador de Telemetria e Discord...
start "BlurMTX - Orquestrador" cmd /c "python server_manager.py"

echo [4/4] Abrindo Painel de Controle e Navegador...
start http://localhost:8080
start "BlurMTX - Painel de Controle" cmd /c "python gui/blur_mtx_control.py"

echo.
echo =====================================================================
echo   ✓ TODOS OS SERVICOS DO BLURMTX FORAM INICIADOS!
echo =====================================================================
echo  - Web Dashboard:     http://localhost:8080
echo  - Painel de Modos:   Janela Aberta
echo  - Orquestrador:      Janela Aberta (Monitorando)
echo.
echo  Agora voce pode abrir o Blur normalmente e criar a sala em LAN.
echo =====================================================================
echo.
timeout /t 5 >nul
endlocal
