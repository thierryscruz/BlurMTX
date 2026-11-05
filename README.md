# BlurMTX v2.2.1 ? Racing Control Center

**[Baixar BlurMTX v2.2.1 para Windows](https://github.com/thierryscruz/BlurMTX/releases/tag/v2.2.1)**

Aplicativo para instalar e iniciar o Blur, configurar LAN e perfil, organizar corridas e consultar estat?sticas. Funciona a partir do jogo base, sem exigir AMAX Emu. Jogo e dados originais n?o acompanham o pacote.

## Instala??o e atualiza??o

1. Feche o Blur e o BlurMTX em cada PC.
2. Baixe `BlurMTX-v2.2.1-Windows.zip`, extraia e execute `BlurMTX.exe`.
3. Selecione a pasta com `Blur.exe` e clique em **Instalar / Atualizar mod**.
4. Configure conex?o e perfil. Use **Iniciar jogo**; o aplicativo fica na bandeja mantendo a coleta ativa. Todos os PCs devem atualizar e manter o aplicativo aberto/minimizado.
5. Clientes que j? possuem o atualizador podem usar **Atualizar Client** quando o aviso aparecer. O download confere SHA-256, faz backup, atualiza o EXE e o mod e reabre o aplicativo.

Se houver outra janela do BlurMTX aberta na mesma pasta, feche-a tamb?m, inclusive na bandeja. O atualizador detecta essas inst?ncias e n?o for?a seu encerramento.

## ID fixo e primeiro cadastro

O coletor cria `MTXMod/client_identity.local.json`. Trocar o nome e reiniciar o jogo mant?m o ID e o hist?rico acumulado. Cada corrida preserva o nome usado na ocasi?o; jogadores com o mesmo nome e IDs diferentes n?o s?o unidos.

**Na primeira inicializa??o do coletor sem ID, os dados locais antigos s?o arquivados e a base ? limpa**, conforme a nova pol?tica de cadastro. O backup fica em `MTXMod/backup/identity_<UUID>/`, com a base SQLite e o journal antigo. Isso impede reimporta??o dos dados anteriores. Perfil, conex?o, Mod Shop e saves do jogo s?o preservados. Depois do cadastro, as atualiza??es mant?m o ID e os dados novos.

N?o distribua o arquivo de identidade para outros jogadores. Ele ? uma identidade do client, n?o um serial de hardware nem autentica??o. IDs corrompidos bloqueiam o cadastro sem apagar novamente a base.

## Novidades

- ID persistente compartilhado pela LAN, inclusive sem dados de combate.
- Imagens estabilizadas segundo o teste do usu?rio; transporte com fragmentos pequenos e prote??o contra imagens antigas.
- Hits compartilhados entre os PCs e agregados sem duplicar o mesmo confronto. Dados incompletos, ausentes ou divergentes s?o sinalizados; n?o h? recupera??o de hits que ningu?m capturou nem identifica??o de armas.
- Bandeja ao iniciar o Blur, com restaurar, painel web e encerrar.
- Verifica??o autom?tica de vers?o em segundo plano e atualiza??o pelo GitHub sem login.
- Pintura LAN, incluindo lend?rios, confirmada pelo usu?rio. BoP permanece experimental, precisa de ativa??o em todos os PCs e calibra??o na pista.

Permita UDP 8081 (avatares), UDP 8082 (hits/identidade) e TCP 8080 para consultar o painel web na LAN. O adaptador local pertence a este PC; os destinos s?o os IPs da sala. O link padr?o dos destinos permanece BLURRPD/main/blur_lan.ini, com consulta pela API para evitar cache antigo.

As estat?sticas aparentemente funcionaram no teste LAN do usu?rio; a cobertura exata ainda merece confer?ncia controlada. O nome continua sendo aplicado ap?s reiniciar o jogo. A janela ? redimension?vel, inicia em 800?600 e mant?m o cr?dito **Developed By: Treex?**.

O execut?vel n?o ? assinado digitalmente; o Windows pode mostrar SmartScreen. O pacote p?blico cont?m execut?vel, instru??es e hashes; n?o inclui fontes Python soltos, credenciais ou dados pessoais. Lua/HTML s?o recursos necess?rios. C?digo-fonte mantido no reposit?rio privado.
