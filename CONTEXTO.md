# Contexto do Projeto — JJS Ladder Bot

## O que é este projeto
Bot para Discord que gerencia um torneio ladder (escada) do jogo **Jujutsu Shenanigans** (Roblox).
A tabela é atualizada automaticamente em um canal fixado do Discord sempre que uma partida é registrada.

---

## Estrutura do torneio

### Grupos (divisões)
| Grupo | Nome   | Vagas | Nível       |
|-------|--------|-------|-------------|
| 0     | Elite  | 5     | Mais forte  |
| 1     | Grupo 1| 10    |             |
| 2     | Grupo 2| 20    |             |
| 3     | Grupo 3| 20    |             |
| 4     | Grupo 4| 20    | Mais fraco  |

### Regras do sistema ladder
- Jogadores novos entram sempre no **último lugar do Grupo 4**
- Desafio padrão: você só pode desafiar o jogador **imediatamente acima** de você
- Ganhou → **sobe uma posição** (troca de lugar com o perdedor)
- **3 vitórias seguidas** → pode desafiar **qualquer jogador da sua divisão**
- Vencer o **1º colocado da divisão** → jogador escolhe:
  - Ficar como **1º da divisão atual**
  - Subir para o **último lugar da divisão acima**
- Ao subir de divisão, a sequência de vitórias é zerada

---

## Decisões técnicas já tomadas
- Linguagem: **Python** com `discord.py 2.3.2`
- Dados salvos em **JSON local** (`dados.json`)
- Comandos **slash** (`/comando`)
- Hospedagem: **Railway** ou **Render** (grátis, 24/7)
- Tabela exibida como **mensagem editada** num canal fixado (não manda nova mensagem toda vez)
- ID da mensagem da tabela salvo em `tabela_msg_id.txt`

---

## Arquivos do projeto
```
jjs-ladder-bot/
├── bot.py                # código principal do bot
├── dados.json            # dados dos jogadores (gerado automaticamente)
├── tabela_msg_id.txt     # ID da mensagem da tabela (gerado automaticamente)
├── requirements.txt      # dependências Python
├── .env.example          # modelo das variáveis de ambiente
├── .gitignore            # ignora .env, dados.json, tabela_msg_id.txt
├── GUIA.md               # passo a passo de instalação para leigo
└── CONTEXTO.md           # este arquivo
```

---

## Variáveis de ambiente necessárias
| Variável         | Descrição                                      |
|------------------|------------------------------------------------|
| `DISCORD_TOKEN`  | Token do bot (Discord Developer Portal)        |
| `TABELA_CANAL_ID`| ID do canal onde a tabela será exibida/editada |

---

## Comandos implementados

### Jogadores
| Comando | Descrição |
|---------|-----------|
| `/entrar` | Entra no torneio (Grupo 4, último lugar) |
| `/tabela` | Mostra a tabela no chat |
| `/perfil [@jogador]` | Estatísticas do jogador |
| `/ajuda` | Lista todos os comandos |

### Admins (requer permissão de administrador ou manage_guild)
| Comando | Descrição |
|---------|-----------|
| `/adicionar @jogador grupo [posicao]` | Adiciona jogador em grupo/posição específica |
| `/resultado @vencedor @perdedor` | Registra resultado de uma partida |
| `/subir @jogador` | Promove jogador para a divisão acima |
| `/remover @jogador` | Remove jogador do torneio |

---

## Comportamento da tabela
- Exibida como bloco de código no Discord (texto monoespaçado)
- Atualizada automaticamente após cada `/resultado`, `/subir`, `/adicionar`, `/remover`, `/entrar`
- Mostra: posição, nome, vitórias, derrotas, sequência de vitórias
- Indicadores visuais:
  - 👑 = 1º colocado da divisão
  - 🔴 = último colocado da divisão
  - 🔥 = jogador com 3+ vitórias seguidas

---

## O que ainda pode ser implementado (ideias futuras)
- [ ] Screenshot automático da tabela como imagem (Playwright/Puppeteer)
- [ ] Comando `/desafiar @jogador` para o próprio jogador solicitar partida
- [ ] Log de partidas em canal separado
- [ ] Sistema de temporadas (resetar tudo a cada X semanas)
- [ ] Limite de partidas por dia por jogador
- [ ] Notificação por DM quando alguém te desafia

---

## Perfil do dono do projeto
- Não tem experiência com programação
- Usa Git Bash e Claude Code no terminal
- Objetivo: subir o projeto no GitHub e hospedar no Railway

## Como continuar com Claude Code
Abra o terminal na pasta do projeto e rode:
```bash
claude
```
O Claude Code vai ler este arquivo e já saberá todo o contexto do projeto.
