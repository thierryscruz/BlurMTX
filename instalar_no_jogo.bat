@echo off
setlocal EnableDelayedExpansion
title BlurMTX - Instalador no Jogo
color 0b

echo =====================================================================
echo   BlurMTX - Instalador do Engine Plugin no Blur [2010]
echo =====================================================================
echo.

set "GAME_DIR=E:\Blur(tm)"
set "PLUGIN_DIR=!GAME_DIR!\amax\plugins\blur_mtx"
set "PLUGINS_FILE=!GAME_DIR!\amax\plugins\plugins.lua"

if not exist "!GAME_DIR!\Blur.exe" goto :err_no_game

if not exist "!PLUGIN_DIR!" (
    echo [1/3] Criando pasta do plugin...
    mkdir "!PLUGIN_DIR!"
) else (
    echo [1/3] Pasta do plugin ja existe.
)

echo [2/3] Copiando arquivos do BlurMTX para o jogo...
copy /Y "E:\BlurMTX\engine\blur_mtx.lua" "!PLUGIN_DIR!\blur_mtx.lua" >nul
copy /Y "E:\BlurMTX\blur_mtx.json" "!PLUGIN_DIR!\blur_mtx.json" >nul
copy /Y "E:\BlurMTX\tracks.json" "!PLUGIN_DIR!\tracks.json" >nul

echo [3/3] Registrando BlurMTX no plugins.lua do jogo...
findstr /C:"blur_mtx.blur_mtx" "!PLUGINS_FILE!" >nul
if errorlevel 1 (
    copy /Y "!PLUGINS_FILE!" "!PLUGINS_FILE!.bak" >nul
    python -c "content = open(r'!PLUGINS_FILE!', 'r', encoding='utf-8').read(); content = content.replace('return {', 'return {\n\trequire(\"blur_mtx.blur_mtx\"),'); open(r'!PLUGINS_FILE!', 'w', encoding='utf-8').write(content)"
    echo  -^> Plugin registrado com sucesso em plugins.lua!
) else (
    echo  -^> BlurMTX ja estava registrado em plugins.lua.
)

echo.
echo =====================================================================
echo   BlurMTX INSTALADO COM SUCESSO!
echo =====================================================================
echo  - Rotacao Automatica de Pistas ativada.
echo  - Voltas personalizadas por circuito ativadas.
echo  - Modo de Start duplo [Automatico ou Manual] integrado.
echo  - Telemetria de combate estilo AMX Mod X pronta para registrar partidas.
echo.
echo  Para alterar mapas, voltas ou regras, execute:
echo  E:\BlurMTX\Abrir_Painel_Controle.bat
echo =====================================================================
echo.
goto :end

:err_no_game
echo [ERRO] O diretorio do Blur nao foi encontrado em: !GAME_DIR!
echo Verifique o caminho da instalacao do jogo.
echo.

:end
endlocal
