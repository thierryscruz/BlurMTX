# BlurMTX — Windows

Painel de configuração e estatísticas LAN para Blur (2010).

**[Baixar BlurMTX v1.3.0](https://github.com/thierryscruz/BlurMTX/releases/tag/v1.3.0)**

Este repositório distribui a versão compilada. Use o arquivo
`BlurMTX-v1.3.0-Windows.zip` na seção Releases; os arquivos automáticos
“Source code” do GitHub não contêm o aplicativo.

## Instalação

1. Tenha Blur e o carregador AMAX compatível já instalados, incluindo
   `amax/init.lua`, `lua5.1.dll` e `amax/dlls/lua_hooks.asi`.
2. Extraia o ZIP em uma pasta gravável. Ele contém o EXE e as instruções.
3. Abra `BlurMTX.exe`. Os recursos locais são criados em `MTXMod/`.
4. No painel, clique em **Pasta do jogo / Instalar mod**, selecione a pasta do
   jogo e instale com o Blur fechado. Só extrair o ZIP não instala a integração.
5. Abra o jogo e entre no lobby LAN. Ajuste regras e playlist pelo painel web.

Não apague os arquivos do jogo. O instalador preserva backup antes de substituir
arquivos. Preferências ficam em `MTXMod/config.local.json` e estatísticas em
`MTXMod/data/`. Preserve essas pastas ao atualizar.

## Uso

- Painel: `http://127.0.0.1:8080`; consulta de estatísticas na rede local:
  `http://IP-DO-PC:8080`. Administração requer acesso pelo painel local.
- O servidor roda no EXE em segundo plano, sem CMD e sem exigir Python instalado.
- Fechar a aba mantém o servidor ativo. Use **Encerrar painel** para pará-lo;
  abra o EXE para iniciar novamente. Diagnósticos: `MTXMod/app.log`.
- Regras básicas, avançadas e power-ups; playlist com voltas por pista;
  configuração de lendários e multiclasse; resultados e ranking SQLite.
- Mudanças são aplicadas no lobby livre. Durante a corrida, aguardam o retorno.
- **Voltas padrão** vale para novas entradas. Ajuste pistas existentes na aba
  **Playlist** se quiser testar com uma volta.
- LAN integrada à DLL: broadcast e seleção de adaptador. O ASI antigo é guardado
  no backup. As opções de `blur_lan.ini` são preservadas.

## Limites desta versão

O resumo apareceu e nomes/classificação foram registrados em um teste com bots.
Nêmesis/rival não foi fornecido nesse teste. A captura detalhada de armas/acertos
continua incompleta; o balanceamento físico das classes não está implementado.
Solo sem bots segue adiado. Lendários, multiclasse, todas as associações de pistas
e LAN entre dois PCs ainda precisam de homologação no jogo.

O pacote não inclui executável, DLL Lua ou outros arquivos originais do jogo.
Consulte as notas da release e confira o SHA-256 antes de substituir sua versão.
