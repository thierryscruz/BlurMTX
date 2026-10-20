@echo off
setlocal EnableDelayedExpansion
title BlurMTX - Desinstalador do Jogo
color 0c

echo =====================================================================
echo   BlurMTX - Desinstalador do Plugin no Blur [2010]
echo =====================================================================
echo.

set "GAME_DIR=E:\Blur(tm)"
set "PLUGIN_DIR=!GAME_DIR!\amax\plugins\blur_mtx"
set "PLUGINS_FILE=!GAME_DIR!\amax\plugins\plugins.lua"

echo [1/2] Removendo registro do BlurMTX em plugins.lua...
if exist "!PLUGINS_FILE!" (
    python -c "content = open(r'!PLUGINS_FILE!', 'r', encoding='utf-8').read(); content = content.replace('\trequire(\"blur_mtx.blur_mtx\"),\n', ''); open(r'!PLUGINS_FILE!', 'w', encoding='utf-8').write(content)"
    echo  -^> Registro removido com sucesso.
)

echo [2/2] Removendo pasta do plugin...
if exist "!PLUGIN_DIR!" (
    rd /s /q "!PLUGIN_DIR!"
    echo  -^> Pasta do plugin removida.
)

echo.
echo =====================================================================
echo   BlurMTX foi desinstalado do jogo com sucesso!
echo =====================================================================
echo.
endlocal
