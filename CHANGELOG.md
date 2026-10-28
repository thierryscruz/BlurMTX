# BlurMTX v1.4.0 — 28/10/2026

- Launcher com botão Iniciar Blur, configuração LAN e painel Web explícito; servidor sem CMD.
- Atualização do IP do host por HTTPS, com link BLURRPD padrão nas novas instalações e preservação das preferências existentes.
- Básico e playlist na mesma tela; mapa e voltas acompanham a rotação, com prioridade das edições salvas no Básico para a pista selecionada.
- Estatísticas como tela inicial: IDs de partidas, filtros independentes por datas/ID, resultados da última partida e combate acumulado por atacante/vítima.
- Captura validada de totais de hits e confrontos, sem identificar armas; resumo LAN corrigido para mostrar nomes e rivais.
- Novas instalações ativam a opção de lendários por padrão.
- Correções no envio das regras pelo host e no fluxo nativo de largada com participantes.
- Processos independentes do PyInstaller para evitar compartilhamento da pasta temporária entre launcher e painel.

Validação: testes Python, Lua 5.1, controlador JavaScript, API/banco, DLL x86, instalação autônoma e ZIP compilado em pasta diferente. Nomes/tempos/rivais foram confirmados na tela do jogo e uma matriz real de hits com bots foi lida e conferida. Ainda falta testar a coleta automática completa em nova corrida e a rotação corrigida entre dois PCs.

Limites: sem contagem por arma, sem BoP físico; solo sem bots adiado. Nem todas as pistas e opções foram homologadas no jogo. Atualize o mesmo pacote em todos os PCs. Requer Blur e carregador AMAX compatível; não inclui arquivos do jogo. EXE sem assinatura digital: pode haver aviso do SmartScreen.

---

# BlurMTX v1.3.0 — 27/10/2026

- Painel web com regras básicas, avançadas, power-ups, playlist e estatísticas SQLite.
- Executável autônomo com recursos embutidos, ícone e servidor sem janela de console.
- Encerramento do servidor pelo painel local autorizado.
- Janela nativa exclusiva de instalação; caminhos relativos à pasta do aplicativo.
- Instalação com backup, verificação de hashes e preservação das preferências locais.
- LAN integrada à DLL; ASI anterior arquivado e blur_lan.ini preservado.
- Catálogo agrupado por cidade/rota; aliases conflitantes retirados e auditoria nativa no lobby.
- Resumo pós-corrida visível, confirmado pelo usuário; resultados com nomes capturados em corrida com bots.
- Leitura do tempo formatado pelo jogo, incluindo marcação de fonte.

Validação: testes Python, Lua 5.1, controlador JavaScript, instalação do ZIP movido,
painel HTTP, encerramento do processo e subsistema gráfico do EXE.

Limitações: captura detalhada de combate e BoP físico incompletos; solo sem bots
adiado; lendários, multiclasse, todos os pares de pista e LAN entre dois PCs ainda
precisam de homologação. Nêmesis/rival não foi fornecido pelo jogo no teste com bots.
Requer Blur e carregador AMAX compatível já instalados; arquivos do jogo não são distribuídos.

Distribuição compilada: https://github.com/thierryscruz/BlurMTX/releases/tag/v1.3.0
Código-fonte mantido separadamente no repositório privado autorizado.
