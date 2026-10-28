# BlurMTX v1.4.0 — Windows

**[Baixar BlurMTX v1.4.0](https://github.com/thierryscruz/BlurMTX/releases/tag/v1.4.0)**

Este repositório distribui somente o compilado. Baixe `BlurMTX-v1.4.0-Windows.zip` em Releases; os arquivos automáticos Source code não contêm o aplicativo.

## Instalação

1. Tenha Blur e AMAX compatível instalados (incluindo lua5.1.dll e lua_hooks.asi).
2. Extraia o ZIP, abra BlurMTX.exe e selecione a pasta do jogo.
3. Use Instalar / Atualizar com o Blur fechado.
4. Configure a LAN e use Iniciar Blur.
5. Abra o painel Web pelo botão do aplicativo para regras e estatísticas.

## Configurar

- Básico: Corrida/Destruction, mapa, voltas, classe, limite de tempo e rotação.
- Avançado: dano, handicap, respawn, timeout, mods/habilidades e upgrades.
- Power-ups: oito armas, chave geral, aleatoriedade e reaparecimento.
- A playlist fica na mesma tela Básico: adicionar, remover, ativar, ordenar e definir voltas por pista.
- Mapa e voltas do Básico acompanham a rotação confirmada pelo jogo, sem sobrescrever edições pendentes. Ao salvar, os valores do Básico prevalecem para a pista selecionada; as outras mantêm suas voltas individuais.
- Carros: catálogo liberado, incluindo lendários, e classes A/B/C/D juntas.
- Novas instalações deixam a opção de lendários ativada por padrão; preferências existentes são preservadas.
- Estatísticas: ranking, histórico, resultados e nêmesis/rival.

As habilidades individuais continuam no Mod Shop; o painel controla a permissão
de usar mods, como a tela original de regras. Em Destruction, use uma arena compatível.
O catálogo ainda precisa ser conferido no jogo para todas as rotas.

Pressione Salvar e aplicar no lobby. O jogo consulta a nova versão aproximadamente
a cada segundo no lobby livre. Durante uma corrida, as alterações aguardam o retorno.
Mapa, voltas e regras não exigem reiniciar; a instalação inicial do novo código exige
reiniciar uma vez. O painel informa quando o jogo confirmou a versão salva.

Os padrões públicos ficam em MTXMod/config.json e as preferências em MTXMod/config.local.json. A entrega ao jogo usa blur_mtx_config.lua com gravação
atômica. Salve pelo painel ou launcher para atualizar também a versão da configuração.

## Estatísticas e limites

O mod grava <pasta do jogo>/MTXMod/events.jsonl. O painel ingere esses eventos em
MTXMod/data/stats.db, inclusive eventos anteriores à sua abertura, sem duplicar partidas.

A tela de resumo foi conferida no jogo: nomes, tempos e rivais apareceram após a correção dos textos LAN. Uma captura real com bots permitiu ler os hits de todos os participantes, nos dois sentidos, e os acertos por adversário. O coletor valida participantes, reciprocidade dos contadores e os maiores valores contra nêmesis/presa antes de gravar os totais.

O painel oferece:

- Todas as corridas com ID numérico local estável.
- Resultados, nêmesis/rival, hits por piloto e confrontos da última partida.
- Combate acumulado: soma dos hits por atacante e vítima entre partidas.
- Visão geral, ranking e recordes por pista/piloto.
- Filtros independentes de datas e ID em cada bloco; combate também filtra atacante. Sem filtros, os detalhes mostram a última partida; com filtros, a mais recente que atende à seleção. Datas incluem os dois extremos.

O coletor de hits lê memória somente no estado de resultados da partida atual, protegido por hash e assinatura do executável mapeado; não modifica o processo. Outras versões de Blur.exe precisam de mapeamento. Não identifica armas nem inventa eventos individuais a partir dos totais. Campos ausentes ficam vazios; carro e melhor volta só são usados quando fornecidos pelo jogo. DNF/timeout não recebe pontos.

Use **Iniciar Blur** para manter o coletor em segundo plano. A coleta integrada completa em uma nova corrida e a sincronização entre dois PCs ainda precisam de validação no jogo. Testes automatizados não substituem essa conferência. Os IDs de partidas são locais ao banco de cada instalação, sem sincronização central de bancos.

O desbloqueio de carros usa consultas da garagem LAN, sem cheats de progresso salvo.
Seleção e aceitação efetiva dos lendários ainda precisam de validação no jogo.
Liberar classes juntas não aplica BoP. O nivelamento de velocidade/aceleração está
bloqueado porque ainda não há API confirmada que preserve as demais características.


## LAN integrada

As funções do antigo blur_lan.asi (broadcast para IPs específicos e seleção do
adaptador de rede) estão compiladas no d3d9.dll do BlurMTX. O instalador guarda
amax/dlls/blur_lan.asi no backup e o retira da pasta de plugins para evitar hooks
duplicados. Não é necessário distribuir ou carregar esse ASI separadamente.

O arquivo blur_lan.ini ao lado de Blur.exe é preservado. Se precisar definir a
placa ou os outros computadores, crie/edite esse arquivo antes de abrir o jogo:

```ini
[LAN]
BindIP=auto
TargetIPs=127.0.0.1
```

Use em BindIP o IPv4 da placa desejada ou auto; em TargetIPs, os IPv4 dos demais
computadores separados por vírgulas. A comunicação entre dois PCs ainda precisa
de teste no ambiente de rede utilizado.

## IP do host por link

Na janela do aplicativo, preencha IP do adaptador (auto ou seu IPv4 local), IP do
host e, opcionalmente, o link HTTPS de um arquivo público. Use Salvar LAN ou
Atualizar pelo link. Marque a atualização automática para consultar o link a cada
abertura do painel pelo EXE, inclusive quando o servidor do painel já estiver aberto.
O instalador também cria blur_lan.ini quando ele não existe.

O arquivo remoto mais simples contém apenas o IPv4 do host, por exemplo:

```text
26.10.20.30
```

Também aceita IPs separados por vírgulas/linhas, JSON com target_ips ou um INI
com [LAN] e TargetIPs. O conteúdo remoto altera somente TargetIPs; BindIP continua
local em cada computador. Dados inválidos, páginas HTML ou falhas de rede mantêm
o último INI. A versão anterior fica em MTXMod/blur_lan.previous.ini.

Cada jogador cadastra o mesmo link uma vez. Depois, o organizador atualiza apenas
o arquivo remoto quando o IP mudar. Abra BlurMTX antes do jogo: a DLL lê o INI na
inicialização do Blur, portanto alterações com o jogo aberto exigem reiniciá-lo.

Novas instalações já vêm com atualização automática ativada e este endereço:
`https://raw.githubusercontent.com/thierryscruz/BLURRPD/main/blur_lan.ini`.
É possível trocar ou desativar o link. Preferências já existentes são preservadas.

Use um arquivo público acessível como texto, sem login. No GitHub, copie a URL do
botão Raw na branch que será atualizada; não use um link fixado em um commit.
Um link de visualização do Drive que retorna HTML não será aceito.
Links Raw e blob do GitHub são consultados pela API de conteúdo para evitar
atrasos do cache Raw após uma alteração. Se a API estiver indisponível ou atingir
seu limite, o último INI válido é preservado e o aplicativo informa a falha.
Suas alterações do link e da opção automática ficam em MTXMod/lan.local.json na
pasta do jogo e não acompanham os pacotes públicos; apenas o endereço padrão é distribuído.

## Sincronização da sala

O host envia as regras nativas depois de aplicar mapa, voltas, classe e power-ups,
incluindo a rotação automática. O envio é repetido no retorno ao lobby para cobrir
clientes que ainda estão saindo dos resultados. O cliente mantém as regras
recebidas e não aplica sua playlist local à sala. A largada com outros jogadores
preserva a espera nativa por sincronização; o atalho solo exige um jogador confirmado.

O teste automatizado usa dois ambientes Lua isolados, com um cliente atrasado,
e verifica aplicação antes do envio e consistência após a rotação. A mudança
ainda precisa ser validada em dois PCs. Atualize e instale o mesmo pacote em ambos.

## Segurança e encerramento

O EXE desta versão não possui assinatura Authenticode; o Windows SmartScreen pode mostrar um aviso de aplicativo desconhecido. Assinatura/reputação são independentes dos testes funcionais. Não é necessário desativar a proteção do Windows para instalar o projeto.

Fechar o launcher ou a aba do navegador mantém o servidor de estatísticas funcionando. Para encerrá-lo, use **Encerrar painel** no painel Web local. Feche também o Blur antes de atualizar. O launcher e o painel agora usam extrações temporárias independentes, corrigindo o compartilhamento que podia impedir a limpeza de pastas `_MEI` ao fechar.
