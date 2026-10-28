# BlurMTX v2.0.0 — 28/10/2026

- Racing Control Center migrado para Qt/PySide6, com cenário noturno e logo original de Blur.
- Janela inicial 800×600, redimensionável pelas oito bordas/cantos; opção 1024×768 nas configurações. Ajuste à área útil, páginas sem rolagem e atalhos compactos em janelas estreitas.
- Crédito discreto “Developed By: Treex™” no rodapé lateral.
- Publicação dos destinos LAN pelo aplicativo para organizadores autorizados, com credencial protegida pelo Windows e controle de conflitos por SHA. Clientes continuam lendo o link público sem login.
- Perfil LAN com nome e avatar local; troca entre participantes via UDP 8081. Validação visual entre dois PCs ainda pendente.
- Persistência local dos slots do Mod Shop por cliente. Confirmar no jogo o ciclo de fechar/reabrir.
- Coleta parcial de confrontos humanos quando apenas a linha local é válida, com cobertura identificada; recuperação da última captura recusada somente quando há evidências correspondentes.
- Encerramento do painel/coletor ao fechar o aplicativo, porta exclusiva no Windows e proteção contra módulos antigos externos ao executável.

Validação: suíte Python, testes Qt de geometria/entrada/redimensionamento, monitor pequeno simulado, escalas de tela distintas, Lua 5.1, controlador JavaScript, API/banco, instalação autônoma e ZIP real em outra pasta. O pacote mantém o mesmo executável já testado e instalado localmente.

Limites: sem identificação de armas, sem BoP físico e sem sincronização central de bancos. A coleta LAN, rotação entre dois PCs, perfis e persistência do Mod Shop ainda exigem as conferências no jogo descritas no README. O executável não é assinado digitalmente. Jogo e AMAX não acompanham o pacote.


---

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
