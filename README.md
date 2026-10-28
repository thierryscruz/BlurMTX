# BlurMTX v2.0.0 — Racing Control Center

**[Baixar BlurMTX v2.0.0 para Windows](https://github.com/thierryscruz/BlurMTX/releases/tag/v2.0.0)**

Este repositório distribui somente o compilado. Baixe `BlurMTX-v2.0.0-Windows.zip` em Releases e extraia o conteúdo. Os arquivos automáticos “Source code” do GitHub não contêm o aplicativo. Python e Qt já estão incluídos no executável.

## Instalação e abertura

1. Tenha Blur e AMAX compatível instalados, incluindo `lua5.1.dll` e o carregador Lua existente.
2. Abra `BlurMTX.exe`, selecione a pasta que contém `Blur.exe` e use **Instalar / Atualizar mod** com o jogo fechado.
3. Configure a conexão LAN neste PC e use **Iniciar jogo**. O mesmo aplicativo serve para host e clientes; a sala é criada ou acessada dentro do jogo.
4. Use **Painel web** quando quiser abrir as regras e estatísticas no navegador. O navegador não abre automaticamente ao iniciar o aplicativo.

O instalador preserva configurações, perfis, loadouts e estatísticas, faz backup dos arquivos substituídos e não altera `Blur.exe`. A instalação pode ser movida para outra pasta; os caminhos não são fixos.

## Janela adaptável

- Abre em **800×600**, centralizada e sem maximizar. Em monitores menores, limita o tamanho inicial à área útil deixando uma margem.
- Arraste qualquer borda ou canto para redimensionar; os controles se ajustam sem barras de rolagem.
- Em **Configurações**, escolha **800×600** ou **1024×768**, respeitando a área útil do monitor.
- Em janelas estreitas, a barra lateral e os atalhos usam ícones. Passe o mouse para ver os nomes.
- Cenário noturno, logo original de Blur e crédito discreto **Developed By: Treex™**.

## LAN e atualização do host

O campo **Adaptador local** pertence a este computador; **Host / destinos** contém os IPv4 da sala, separados por vírgula. O antigo `blur_lan.asi` foi integrado ao mod, preservando `blur_lan.ini` e fazendo backup do ASI anterior quando encontrado.

Novas instalações usam este link público por padrão:

`https://raw.githubusercontent.com/thierryscruz/BLURRPD/main/blur_lan.ini`

A atualização automática consulta o link ao abrir e antes de iniciar o jogo. **Atualizar agora** força uma consulta. Apenas os destinos são sincronizados; o adaptador local é preservado. Se a consulta falhar, o último INI válido é mantido. Alterações da LAN exigem reabrir o jogo.

Organizadores podem publicar os destinos pelo botão **Salvar conexão**: autorize o GitHub em Configurações e marque **Publicar no GitHub ao salvar** na página Conexão LAN. É necessário acesso de escrita ao repositório. O token fica no Gerenciador de Credenciais do Windows. Jogadores apenas leem o link público, sem login. Iniciar, atualizar pelo link e instalar não publicam alterações automaticamente. Não há escrita anônima.

## Regras e playlist no painel web

- Básico e playlist na mesma tela: modo, mapa, voltas, classe, limite de tempo e rotação.
- Avançado: dano, handicap, respawn, timeout, mods/habilidades e upgrades.
- Power-ups: oito armas, chave geral, aleatoriedade e reaparecimento.
- Carros lendários ativados por padrão em instalações novas; preferências existentes são preservadas.
- Mapa e voltas acompanham a rotação. Ao salvar, os valores editados no Básico prevalecem para a pista selecionada.

Use **Salvar e aplicar no lobby**. Durante uma corrida, as mudanças aguardam o retorno ao lobby livre. O host transmite as regras; os clientes não aplicam sua playlist local à sala. Atualize todos os PCs para a mesma versão. A rotação entre dois PCs ainda precisa de nova conferência no jogo.

O painel abre em `http://127.0.0.1:8080`. Pela rede, `http://IP-DO-PC:8080` oferece consulta; a edição exige acesso local autorizado. O aplicativo não inicia um servidor dedicado do jogo: ele prepara a LAN e mantém o painel/coletor de estatísticas.

## Estatísticas e encerramento

O painel mostra corridas com ID local, resultados, nêmesis/rival, hits por piloto e confrontos da última partida. Há combate acumulado por atacante/vítima, ranking e filtros independentes de datas, ID e atacante conforme o bloco. Dados ausentes permanecem vazios.

A matriz completa de hits só é aceita quando validada. Se apenas a linha do jogador local for válida, uma corrida com dois jogadores permite registrar os dois sentidos; com três ou mais, essa captura cobre apenas confrontos envolvendo o piloto local. O painel informa a cobertura. Não há identificação por arma nem estatísticas inventadas entre jogadores remotos. A leitura nativa é limitada ao executável verificado e ao estado de resultados.

Os dados ficam em `MTXMod/data/stats.db`; cada PC tem seu próprio banco e seus IDs. Não há sincronização central automática de bancos. Capturas antigas sem contadores preservados não podem ser reconstruídas.

**Mantenha o aplicativo aberto ou minimizado durante as corridas.** Fechar a aba do navegador mantém o coletor ativo; fechar o aplicativo pelo X encerra também o painel/coletor da mesma instalação. **Encerrar painel** interrompe somente o servidor/coletor. O jogo continua aberto. O servidor usa porta exclusiva para evitar instâncias duplicadas.

## Perfil e Mod Shop

Em **Perfil**, escolha nome e imagem e salve com o jogo fechado. São aceitos nomes de 1 a 15 caracteres sem acentos; a imagem é normalizada localmente para 64×64. Use nomes distintos. A troca de avatares LAN usa UDP 8081 e não altera a conta ou a imagem do site AMAX. **Usar perfil original** desativa a personalização. A exibição de nome/avatar entre dois PCs ainda precisa de validação no jogo.

O Mod Shop salva os três loadouts personalizados e a seleção ativa por cliente em `MTXMod/loadouts.local.txt`. Os slots são restaurados; nomes personalizados dos loadouts não são restaurados. A persistência foi testada automaticamente, mas o ciclo de fechar/reabrir o cliente ainda precisa de confirmação no jogo.

## Limites e compatibilidade

- Liberar classes A/B/C/D juntas não aplica nivelamento de velocidade/aceleração (BoP).
- Melhorias de bots, Discord e correção do modo solo sem bots estão fora do escopo atual.
- Alguns mapas/combinações, lendários, perfis e sincronização LAN ainda exigem teste no jogo. Testes automatizados não substituem essa validação.
- O executável não tem assinatura Authenticode; o SmartScreen pode mostrar aviso de aplicativo desconhecido.
- Licenças do Qt/PySide6 e referências de código-fonte ficam em `MTXMod/licenses` após a primeira abertura. A [logo de Blur](https://www.steamgriddb.com/logo/155671) e as marcas pertencem aos respectivos titulares.

Os pacotes não incluem o jogo, AMAX, tokens, IPs locais, perfis pessoais, bancos, logs ou backups. Confira os arquivos baixados com `SHA256SUMS.txt` na release.
