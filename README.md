# BlurMTX v2.1.0 — Racing Control Center

**[Baixar BlurMTX v2.1.0 para Windows](https://github.com/thierryscruz/BlurMTX/releases/tag/v2.1.0)**

Aplicativo para instalar e iniciar o Blur com integração LAN, perfil local, regras de corrida, playlist e estatísticas web. O pacote Windows inclui Python, Qt e o runtime Lua necessário; não exige AMAX Emu nem plugins copiados de outra máquina. O jogo e seus dados não acompanham a distribuição.

## Instalar ou atualizar

1. Feche o Blur e o BlurMTX.
2. Baixe `BlurMTX-v2.1.0-Windows.zip` em Releases e extraia em uma pasta. Os downloads automáticos “Source code” do GitHub não contêm o executável.
3. Execute o novo `BlurMTX.exe`, selecione a pasta que contém `Blur.exe` e clique em **Instalar / Atualizar mod**.
4. Em **Conexão LAN**, use **auto** no adaptador local ou um IPv4 pertencente a este PC. Host/destinos são os endereços dos participantes; não copie o IP do host para o adaptador do cliente.
5. Configure o perfil e use **Iniciar jogo**. O mesmo aplicativo atende host e clientes; criar ou entrar na sala continua sendo feito dentro do jogo.

A instalação cria backup e verifica hashes, preservando preferências, perfil, INI, loadouts e estatísticas. Não altera `Blur.exe` e não fixa a pasta de instalação. Atualize todos os participantes para a mesma versão.

## Novidades da versão 2.1.0

- Loader nativo **v4.2 ADAPTER-FIX**: corrige a cópia de 648 bytes em estruturas de adaptadores de 640 bytes que podia criar um ciclo infinito ao abrir a LAN. O caso foi reproduzido em teste e o usuário confirmou a entrada na LAN no notebook afetado após a correção.
- Instalação independente a partir do jogo base, com bootstrap Lua próprio e compatibilidade entre os objetos internos do jogo e o runtime incluído.
- Instalações compiladas não criam `launcher.py` nem copiam fontes Python. Atualizações arquivam no backup apenas módulos antigos conhecidos do BlurMTX e seus caches, preservando scripts de terceiros e checkouts de desenvolvimento.
- Estatísticas organizadas por botões: um bloco por vez, filtros independentes de data/ID e combate acumulado por período.
- Mod Shop local: persistência dos quatro loadouts, incluindo Loadout 1, e proteção contra o reset nativo sobrescrever as preferências.
- Classes misturadas e BoP local experimental; permissão de pintura LAN experimental, inclusive para lendários.

## Aplicativo, perfil e LAN

A janela começa em 800×600, permite redimensionamento e ajusta as páginas sem rolagem. Configurações também oferece 1024×768. A interface usa Qt/PySide6, cenário noturno, logo de Blur e o crédito **Developed By: Treex™**.

O perfil permite nome LAN e imagem local. O nome deve ter de 1 a 15 caracteres ASCII válidos. A troca de avatares entre participantes usa UDP 8081; a conferência visual entre todas as máquinas continua recomendada. O Mod Shop é salvo por cliente; não depende do host.

Novas instalações ativam lendários, usam adaptador **auto**, deixam BoP/pintura experimental desativados e adotam o link público abaixo com atualização automática dos destinos:

`https://raw.githubusercontent.com/thierryscruz/BLURRPD/main/blur_lan.ini`

A consulta ocorre ao abrir e antes de iniciar o jogo. Apenas os destinos são sincronizados; o adaptador local é preservado. Links GitHub usam a API de conteúdo para evitar versões antigas do Raw em cache. Se a consulta falhar, o último INI válido é mantido. Preferências já existentes não são resetadas.

Organizadores com acesso de escrita podem autorizar o GitHub em Configurações e marcar **Publicar no GitHub ao salvar**. A publicação ocorre somente no salvamento explícito; jogadores apenas consultam o link, sem login. Credenciais ficam no Gerenciador de Credenciais do Windows, não no pacote. Alterações de LAN exigem reiniciar o jogo.

## Regras e playlist

**Painel web** abre `http://127.0.0.1:8080`. O navegador não abre sozinho ao iniciar o aplicativo. Pela LAN, `http://IP-DO-PC:8080` permite consulta; a edição é autorizada localmente.

- Básico e playlist na mesma tela: modo, mapa, voltas, classe e rotação sequencial/aleatória.
- Avançado: dano, handicap, respawn, timeout, mods/habilidades e upgrades.
- Power-ups: oito armas, chave geral, aleatoriedade e reaparecimento.
- Carros: lendários, classes misturadas e opções experimentais.

Os campos do Básico acompanham a rotação confirmada. Ao salvar, as edições do Básico prevalecem para a pista selecionada; as demais mantêm suas voltas. Use **Salvar e aplicar no lobby**: mudanças durante uma corrida aguardam o retorno. O host transmite as regras; clientes não impõem sua playlist à sala.

## Estatísticas e encerramento

O coletor mantém `MTXMod/events.jsonl` e SQLite em `MTXMod/data/stats.db`, com IDs locais de partida e ingestão sem duplicação. O painel oferece histórico, resultados, nêmesis/rival, hits por piloto, confrontos da partida e totais por adversário no período. Filtros são independentes por bloco.

Os dados de combate são validados antes de gravar. Com bots foi possível capturar uma matriz completa. Em algumas partidas entre humanos, o jogo fornece apenas a linha local confiável: nesse caso aparecem os confrontos envolvendo o piloto local, não os confrontos entre todos os demais. Não há sincronização central dos bancos nem identificação de armas; dados indisponíveis permanecem vazios.

**Iniciar jogo** inicia também o painel/coletor em segundo plano, sem janela de CMD. Mantenha o aplicativo aberto ou minimizado durante as corridas. **Encerrar painel** para o coletor; fechar o aplicativo encerra os processos da mesma instalação, sem fechar o Blur.

## Recursos experimentais e limites

O BoP altera escala de torque e relação final em B/C/D usando referências da classe A, preservando os demais campos de física. Continua experimental: equivalência de velocidade/aceleração exige calibração em pista. Todos os PCs precisam da versão atual e da opção ativada localmente; o host ainda não sincroniza esse sinalizador.

A opção de pintura libera a permissão na garagem LAN; materiais especiais podem não responder. A mudança visual nos lendários ainda não foi confirmada. Solo sem bots e melhorias de bots permanecem fora do escopo. O catálogo completo ainda exige conferência de todas as rotas/modos.

O carregador depende do executável Blur 1.2 verificado. Outras versões exigem mapeamento. O aplicativo não é assinado digitalmente; o SmartScreen pode continuar avisando.

## Arquivos e licenças

O ZIP público contém somente `BlurMTX.exe` e este README. Após instalar, Lua/HTML/configurações, bibliotecas e licenças ficam externos porque são recursos usados pelo jogo e pelo painel. Não há arquivos Python de código-fonte soltos numa instalação compilada limpa. Empacotamento não equivale a criptografia ou proteção contra engenharia reversa.

Qt/PySide6/Shiboken são distribuídos sob suas licenças; Lua 5.1.5 sob MIT. Avisos, textos e referências de origem ficam em `MTXMod/licenses`. Não há redistribuição de plugins AMAX originais, dados de partida, credenciais ou arquivos do jogo.
