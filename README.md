# 🏎️ BlurMTX — Dedicated Server & Match Analytics Suite
> **A complete dedicated server, map rotation controller, and real-time combat analytics engine (AMX Mod X style) for Blur (2010) on PC.**

[![Platform](https://img.shields.io/badge/Platform-Windows%20PC-00D2FF?style=for-the-badge&logo=windows)](https://github.com)
[![Game](https://img.shields.io/badge/Game-Blur%20(2010)-FF007F?style=for-the-badge)](https://github.com)
[![Python](https://img.shields.io/badge/Python-3.8+-10B981?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Status](https://img.shields.io/badge/Status-Ready%20to%20Play-FF6B00?style=for-the-badge)](https://github.com)

---

## 🌟 O que é o BlurMTX?

O **BlurMTX** transforma qualquer sala multiplayer do clássico **Blur (2010)** em um servidor profissional e competitivo estilo *AMX Mod X*:

* 🏁 **Rotação Automática de Pistas:** Playlist completa dos 18 circuitos oficiais com seleção por checklist e voltas personalizáveis de 1 a 99 voltas!
* ⏱️ **Start Duplo (Automático vs Manual):** Escolha entre largada automática com contagem regressiva ou largada manual onde o host aguarda todos os jogadores se conectarem antes de iniciar.
* 🏎️ **Balance of Performance (BoP):** Garagem multi-classe desbloqueada! Pilote um Fusca (Classe D) nivelado proporcionalmente para disputar de igual para igual contra um Astra ou Viper (Classe A), preservando o peso e estilo original do carro.
* ⚡ **1-Clique Presets:** Carregue modos de jogo pré-configurados instantaneamente:
  * 🏆 **F1 Grand Prix** (15 voltas, sem armas agressivas, dano baixo)
  * 💣 **Caos Demolition Derby** (Shunts e Minas em abundância, respawn acelerado)
  * 🚀 **Pura Velocidade / Clean Racing** (Apenas Nitro, foco em pilotagem limpa)
  * 🏎️ **Clássicos Multi-Class BoP** (Fuscas e Opalas nivelados com Classe A)
  * ⚡ **Blur Oficial Padrão** (Regras originais balanceadas)
* 🎯 **Matriz de Combate ("Quem atirou em quem"):** Registra em tempo real todos os disparos, defesas com escudo e destruições de veículos.
* 🏆 **Classificação Geral do Campeonato:** Pontuação oficial estilo Fórmula 1 ($25, 18, 15, 12, 10, 8, 6, 4, 2, 1$) salva em banco de dados local SQLite.
* 🌐 **Live Web Dashboard Administrativo:** Acompanhe corridas ao vivo e altere pistas, voltas e regras pelo navegador do PC ou pelo celular na rede local (`http://localhost:8080`).
* 📢 **Webhook para Discord:** Transmissão automática do pódio, MVP da corrida e tabela do campeonato para o canal do seu clã/servidor no Discord.

---

## 🚀 Como Instalar e Jogar

### Pré-requisitos
1. Jogo **Blur (2010)** instalado no PC.
2. *(Opcional)* Se não quiser instalar o Python, utilize diretamente o executável **`BlurMTX.exe`** disponível na aba de **Releases** do GitHub!

### Instalação e Uso em 2 Passos (100% Executável)

1. Baixe o pacote do BlurMTX (**`BlurMTX.exe`** ou o zip dos Releases) e extraia em qualquer pasta.
2. Dê um duplo clique no executável:
   ```cmd
   BlurMTX.exe
   ```

Ao abrir:
* 🌐 O **Web Dashboard** abrirá automaticamente no seu navegador em `http://localhost:8080`.
* 🎮 A **Janela de Controle** abrirá com todas as configurações e presets.
* ⚡ No topo da janela, clique no botão **`🎮 Instalar no Blur`** (necessário apenas na 1ª vez para registrar o plugin na pasta do jogo automaticamente).

Pronto! Agora basta abrir o Blur e criar sua sala de corrida multiplayer!

---

## 📱 Controle Remoto pelo Celular (Web Admin)

Você pode controlar o lobby do servidor sem precisar minimizar o jogo:
1. Conecte o celular na mesma rede Wi-Fi do computador do servidor.
2. Abra o navegador do celular e acesse:
   ```text
   http://<IP_DO_SEU_PC>:8080
   ```
3. Pelo celular você pode:
   * Marcar e desmarcar pistas da rotação;
   * Digitar a quantidade de voltas de cada corrida;
   * Ligar/desligar armas e opções da sala;
   * Clicar no botão fixo **"💾 SALVAR CONFIGURAÇÕES NO SERVIDOR"** para aplicar imediatamente.

---

## ⚙️ Configurações e Arquivos

* `blur_mtx.json`: Arquivo central onde todas as regras e preferências ficam salvas.
* `presets.json`: Modos de jogo rápidos em 1 clique.
* `tracks.json`: Metadados das 18 pistas oficiais com limites de voltas.
* `Abrir_Painel_Controle.bat`: Abre apenas a janela visual desktop de configurações.
* `desinstalar_do_jogo.bat`: Remove o plugin do Blur de forma limpa caso deseje desinstalar.

---

## 🤝 Comunidade e Licença
Desenvolvido para manter viva a comunidade competitiva do lendário **Blur (2010)** no PC.
Sinta-se livre para usar em campeonatos, servidores LAN e criar novos modos de jogo!
