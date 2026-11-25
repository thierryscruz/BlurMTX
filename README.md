# BlurMTX — Racing Control Center

Instale o mod, inicie o Blur, configure a conexão e o perfil, organize corridas e consulte estatísticas. Funciona a partir do jogo base compatível, sem exigir AMAX Emu. O jogo não acompanha o pacote.

**[Baixar BlurMTX v2.3.0 para Windows](https://github.com/thierryscruz/BlurMTX/releases/tag/v2.3.0)**

## Instalação

1. Feche o Blur e todas as instâncias do BlurMTX, inclusive na bandeja.
2. Baixe o ZIP da versão 2.3.0, extraia e execute `BlurMTX.exe`.
3. Selecione a pasta que contém `Blur.exe` e clique em **Instalar / Atualizar mod**.
4. Configure conexão e perfil e use **Iniciar jogo**. Mantenha o BlurMTX aberto ou minimizado durante as partidas.

Use o mesmo pacote em todos os PCs participantes. O instalador faz backup dos arquivos substituídos e preserva configurações e dados locais.

## Novidades da versão 2.3.0

- Card **Conexão** com seleção **LAN / INTERNET** e **Client / Host**. LAN continua sendo o padrão.
- Internet experimental por Quick Tunnel: o Host usa o `cloudflared` do sistema; quem entra como Client precisa apenas do link completo da sala. Sem WARP, conta ou domínio.
- Organizadores autorizados podem publicar o link no campo `[Internet] RoomURL` do INI compartilhado. Os IPs LAN ficam separados.
- Caixa **Inicializar na LAN**, desmarcada por padrão. Quando ativada, continua a abertura, usa Skip da conta online e abre o menu LAN, sem entrar em sala.
- Abertura personalizada de 10 segundos em 720p com áudio, embutida no EXE e instalada com backup dos vídeos anteriores.
- Conferência da versão instalada e aviso com download oficial quando o Host não possui `cloudflared`.

**Limites do teste:** a ponte transporta UDP do jogo. O Quick Tunnel continua experimental. Avatares, IDs e hits entre coletores pela internet ainda não são encaminhados. Os recursos de LAN permanecem disponíveis. Compartilhe o link completo, incluindo `#mtx=...`, somente com os participantes.


## Perfil e estatísticas

O Client mantém um ID persistente: mudar o nome e reiniciar o jogo preserva a identidade e o histórico. Não distribua `MTXMod/client_identity.local.json` para outros jogadores.

Na primeira execução do coletor sem ID, a base antiga é arquivada em `MTXMod/backup/identity_<UUID>/` e reiniciada. Depois do cadastro, as atualizações preservam os novos dados. Configurações, avatar, Mod Shop e saves são preservados.

Em LAN, permita UDP 8081 para avatares, UDP 8082 para hits/identidade e TCP 8080 para consultar o painel web. O adaptador local pertence a este PC; os destinos são os IPs dos participantes. BoP continua opcional e experimental.

O pacote público contém executável, instruções e hashes SHA-256. O código-fonte fica no repositório privado. O EXE não possui assinatura digital; o Windows pode apresentar SmartScreen.
