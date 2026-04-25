# 🎮 Guia de Instalação — JJS Ladder Bot

## O que você vai precisar
- Uma conta no **Discord** (você já tem)
- Uma conta no **GitHub** (grátis) → https://github.com
- Uma conta no **Railway** (grátis) → https://railway.app

---

## PASSO 1 — Criar o Bot no Discord

1. Acesse https://discord.com/developers/applications
2. Clique em **"New Application"**
3. Dê um nome (ex: `JJS Ladder`) e clique em **Create**
4. No menu lateral, clique em **"Bot"**
5. Clique em **"Reset Token"** e copie o token — **guarde bem, não compartilhe com ninguém!**
6. Ative as seguintes opções em "Privileged Gateway Intents":
   - ✅ SERVER MEMBERS INTENT
   - ✅ MESSAGE CONTENT INTENT
7. No menu lateral, clique em **"OAuth2" > "URL Generator"**
8. Em "Scopes", marque: `bot` e `applications.commands`
9. Em "Bot Permissions", marque:
   - ✅ Send Messages
   - ✅ Read Messages/View Channels
   - ✅ Manage Messages (para fixar a tabela)
   - ✅ Embed Links
10. Copie a URL gerada e abra no navegador para adicionar o bot ao seu servidor

---

## PASSO 2 — Pegar o ID do canal da tabela

1. No Discord, abra as **Configurações do usuário** → **Avançado**
2. Ative o **Modo Desenvolvedor**
3. Clique com o botão direito no canal onde a tabela vai aparecer
4. Clique em **"Copiar ID do canal"** — guarde esse número

---

## PASSO 3 — Subir o código no GitHub

1. Acesse https://github.com e faça login
2. Clique em **"New repository"** (botão verde ou "+" no canto)
3. Dê um nome (ex: `jjs-ladder-bot`), marque como **Private**, clique em **Create**
4. Clique em **"uploading an existing file"**
5. Arraste os arquivos:
   - `bot.py`
   - `requirements.txt`
   - `dados.json`
   - `.gitignore`
6. Clique em **"Commit changes"**

---

## PASSO 4 — Subir no Railway (hospedagem grátis)

1. Acesse https://railway.app e faça login com sua conta do GitHub
2. Clique em **"New Project"**
3. Escolha **"Deploy from GitHub repo"**
4. Selecione o repositório `jjs-ladder-bot`
5. Clique no projeto criado → vá em **"Variables"** (variáveis de ambiente)
6. Adicione as seguintes variáveis:

   | Nome              | Valor                        |
   |-------------------|------------------------------|
   | `DISCORD_TOKEN`   | o token do passo 1           |
   | `TABELA_CANAL_ID` | o ID do canal do passo 2     |

7. Vá em **"Settings"** → **"Deploy"** e certifique que o comando de start é:
   ```
   python bot.py
   ```
8. Clique em **"Deploy"** — o bot vai ligar em alguns segundos!

---

## PASSO 5 — Adicionar os jogadores iniciais

No Discord, use os comandos de admin para montar a lista:

```
/adicionar @jogador grupo:4 posicao:1
/adicionar @jogador grupo:4 posicao:2
... (repita para todos)
```

Ou deixe os jogadores usarem `/entrar` para entrar sozinhos pelo último lugar do Grupo 4.

---

## 📋 Referência de Comandos

### Jogadores
| Comando | O que faz |
|---------|-----------|
| `/entrar` | Entra no torneio (Grupo 4, último lugar) |
| `/tabela` | Mostra a tabela no chat |
| `/perfil` | Vê suas estatísticas |
| `/perfil @alguém` | Vê as estatísticas de outro jogador |
| `/ajuda` | Lista todos os comandos |

### Admins
| Comando | O que faz |
|---------|-----------|
| `/adicionar @jogador grupo posicao` | Adiciona jogador em grupo/posição específica |
| `/resultado @vencedor @perdedor` | Registra resultado de uma partida |
| `/subir @jogador` | Promove jogador para a divisão acima |
| `/remover @jogador` | Remove jogador do torneio |

---

## 🔥 Como funciona na prática

**Partida normal (escada):**
```
/resultado @Ash @Soot
→ Ash sobe uma posição, sequência +1
→ Tabela atualizada automaticamente no canal
```

**Jogador com 3 vitórias seguidas:**
```
→ Bot avisa que pode desafiar qualquer um
→ Admin registra o desafio especial normalmente com /resultado
```

**Subir de divisão:**
```
→ Jogador vence o 1º da divisão e escolhe subir
→ Admin usa /subir @jogador
→ Jogador vai para o último lugar da divisão acima
```

---

## ❓ Problemas comuns

**Bot não aparece online:**
- Verifique se o TOKEN está correto nas variáveis do Railway
- Veja os logs no Railway (aba "Deployments") para ver o erro

**Tabela não aparece no canal:**
- Verifique se o TABELA_CANAL_ID está correto
- O bot precisa de permissão para enviar mensagens e fixar no canal

**Comandos não aparecem:**
- Aguarde até 1 hora após o primeiro deploy para os comandos aparecerem
- Ou reinicie o deploy no Railway
