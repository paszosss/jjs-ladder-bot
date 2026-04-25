import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

# ─────────────────────────────────────────────
#  CONFIGURAÇÕES — edite aqui antes de subir
# ─────────────────────────────────────────────
TOKEN = os.environ.get("DISCORD_TOKEN", "SEU_TOKEN_AQUI")

# ID do canal onde a tabela será exibida/atualizada
TABELA_CANAL_ID = int(os.environ.get("TABELA_CANAL_ID", "0"))

# ID da mensagem fixada da tabela (preenchido automaticamente na 1ª vez)
TABELA_MSG_ID_FILE = "tabela_msg_id.txt"

# Arquivo onde os dados ficam salvos
DATA_FILE = "dados.json"

# ─────────────────────────────────────────────
#  ESTRUTURA DOS GRUPOS
#  chave = número do grupo, valor = capacidade máxima
# ─────────────────────────────────────────────
GRUPOS = {
    0: {"nome": "Elite",   "max": 5,  "emoji": "👑"},
    1: {"nome": "Grupo 1", "max": 10, "emoji": "🔥"},
    2: {"nome": "Grupo 2", "max": 20, "emoji": "⚡"},
    3: {"nome": "Grupo 3", "max": 20, "emoji": "🌊"},
    4: {"nome": "Grupo 4", "max": 20, "emoji": "🌱"},
}

# ─────────────────────────────────────────────
#  SETUP DO BOT
# ─────────────────────────────────────────────
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree


# ─────────────────────────────────────────────
#  FUNÇÕES DE DADOS
# ─────────────────────────────────────────────
def carregar_dados():
    """Carrega os dados do arquivo JSON."""
    if not os.path.exists(DATA_FILE):
        dados = {str(g): [] for g in GRUPOS}
        salvar_dados(dados)
        return dados
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def salvar_dados(dados):
    """Salva os dados no arquivo JSON."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


def jogador_existe(dados, discord_id):
    """Verifica se o jogador já está em algum grupo."""
    for grupo, jogadores in dados.items():
        for j in jogadores:
            if j["id"] == str(discord_id):
                return True, int(grupo), jogadores.index(j)
    return False, None, None


def encontrar_jogador(dados, discord_id):
    """Retorna (grupo, posição_0indexed, dados_jogador) ou None."""
    for grupo, jogadores in dados.items():
        for i, j in enumerate(jogadores):
            if j["id"] == str(discord_id):
                return int(grupo), i, j
    return None, None, None


# ─────────────────────────────────────────────
#  GERAÇÃO DA TABELA (texto para o Discord)
# ─────────────────────────────────────────────
def gerar_tabela(dados):
    linhas = []
    linhas.append("# 🎮 Jujutsu Shenanigans — Ladder")
    linhas.append(f"*Atualizado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}*\n")

    for g_num, g_info in GRUPOS.items():
        jogadores = dados.get(str(g_num), [])
        emoji = g_info["emoji"]
        nome = g_info["nome"]
        total = len(jogadores)
        maximo = g_info["max"]

        linhas.append(f"## {emoji} {nome}  `{total}/{maximo}`")

        if not jogadores:
            linhas.append("*Nenhum jogador ainda.*\n")
            continue

        linhas.append("```")
        linhas.append(f"{'Pos':<5} {'Jogador':<22} {'V':<5} {'D':<5} {'Sequência'}")
        linhas.append("─" * 52)

        for i, j in enumerate(jogadores):
            pos = i + 1
            nome_j = j["nome"][:20]
            v = j.get("vitorias", 0)
            d = j.get("derrotas", 0)
            seq = j.get("sequencia", 0)

            # Indicadores visuais
            if pos == 1:
                prefixo = "👑"
            elif pos == total:
                prefixo = "🔴"
            elif seq >= 3:
                prefixo = "🔥"
            else:
                prefixo = "  "

            seq_txt = f"{seq}🔥" if seq >= 2 else "-"
            linhas.append(f"{prefixo}{pos:<4} {nome_j:<22} {v:<5} {d:<5} {seq_txt}")

        linhas.append("```\n")

    linhas.append("─" * 40)
    linhas.append("🔥 = 3+ vitórias seguidas → pode desafiar qualquer um da divisão")
    linhas.append("👑 = Líder da divisão  |  🔴 = Último colocado")

    return "\n".join(linhas)


# ─────────────────────────────────────────────
#  ATUALIZAR MENSAGEM FIXADA NO CANAL
# ─────────────────────────────────────────────
async def atualizar_tabela_canal(dados):
    """Edita (ou cria) a mensagem da tabela no canal configurado."""
    if TABELA_CANAL_ID == 0:
        return

    canal = bot.get_channel(TABELA_CANAL_ID)
    if not canal:
        return

    conteudo = gerar_tabela(dados)

    # Tenta carregar o ID da mensagem já existente
    msg_id = None
    if os.path.exists(TABELA_MSG_ID_FILE):
        with open(TABELA_MSG_ID_FILE) as f:
            txt = f.read().strip()
            if txt.isdigit():
                msg_id = int(txt)

    try:
        if msg_id:
            msg = await canal.fetch_message(msg_id)
            await msg.edit(content=conteudo)
        else:
            raise Exception("sem mensagem")
    except Exception:
        # Cria mensagem nova e salva o ID
        msg = await canal.send(conteudo)
        with open(TABELA_MSG_ID_FILE, "w") as f:
            f.write(str(msg.id))
        try:
            await msg.pin()
        except Exception:
            pass


# ─────────────────────────────────────────────
#  VERIFICAÇÃO DE PERMISSÃO
# ─────────────────────────────────────────────
def eh_admin(interaction: discord.Interaction):
    return interaction.user.guild_permissions.administrator or \
           interaction.user.guild_permissions.manage_guild


# ══════════════════════════════════════════════
#  COMANDOS SLASH
# ══════════════════════════════════════════════

# ─────────────────────────────────────────────
#  /adicionar — admin cadastra jogador
# ─────────────────────────────────────────────
@tree.command(name="adicionar", description="[Admin] Adiciona um jogador ao torneio")
@app_commands.describe(
    jogador="Mencione o jogador (@jogador)",
    grupo="Grupo onde o jogador entra (0=Elite, 4=Entrada)",
    posicao="Posição dentro do grupo (deixe em branco = último lugar)"
)
async def cmd_adicionar(
    interaction: discord.Interaction,
    jogador: discord.Member,
    grupo: int,
    posicao: int = None
):
    if not eh_admin(interaction):
        await interaction.response.send_message("❌ Apenas admins podem usar este comando.", ephemeral=True)
        return

    if grupo not in GRUPOS:
        await interaction.response.send_message("❌ Grupo inválido. Use 0, 1, 2, 3 ou 4.", ephemeral=True)
        return

    dados = carregar_dados()
    existe, _, _ = jogador_existe(dados, jogador.id)
    if existe:
        await interaction.response.send_message(f"❌ {jogador.display_name} já está no torneio.", ephemeral=True)
        return

    lista = dados[str(grupo)]
    max_grupo = GRUPOS[grupo]["max"]

    if len(lista) >= max_grupo:
        await interaction.response.send_message(
            f"❌ Grupo {grupo} está cheio ({max_grupo}/{max_grupo}).", ephemeral=True
        )
        return

    novo = {
        "id": str(jogador.id),
        "nome": jogador.display_name,
        "vitorias": 0,
        "derrotas": 0,
        "sequencia": 0,
    }

    if posicao and 1 <= posicao <= len(lista) + 1:
        lista.insert(posicao - 1, novo)
    else:
        lista.append(novo)

    dados[str(grupo)] = lista
    salvar_dados(dados)
    await atualizar_tabela_canal(dados)

    pos_final = lista.index(novo) + 1
    await interaction.response.send_message(
        f"✅ **{jogador.display_name}** adicionado ao **{GRUPOS[grupo]['nome']}** na posição **{pos_final}º**!"
    )


# ─────────────────────────────────────────────
#  /entrar — jogador entra no grupo 4 (último)
# ─────────────────────────────────────────────
@tree.command(name="entrar", description="Entre no torneio! Você começa no último lugar do Grupo 4.")
async def cmd_entrar(interaction: discord.Interaction):
    dados = carregar_dados()
    existe, _, _ = jogador_existe(dados, interaction.user.id)
    if existe:
        await interaction.response.send_message("❌ Você já está no torneio!", ephemeral=True)
        return

    lista = dados["4"]
    if len(lista) >= GRUPOS[4]["max"]:
        await interaction.response.send_message(
            "❌ O Grupo 4 está cheio no momento. Aguarde uma vaga ou contate um admin.", ephemeral=True
        )
        return

    novo = {
        "id": str(interaction.user.id),
        "nome": interaction.user.display_name,
        "vitorias": 0,
        "derrotas": 0,
        "sequencia": 0,
    }
    lista.append(novo)
    dados["4"] = lista
    salvar_dados(dados)
    await atualizar_tabela_canal(dados)

    pos = len(lista)
    await interaction.response.send_message(
        f"✅ **{interaction.user.display_name}** entrou no torneio! "
        f"Você está em **{pos}º lugar** no **{GRUPOS[4]['nome']}**. Bora subir! 🔥"
    )


# ─────────────────────────────────────────────
#  /resultado — admin registra resultado
# ─────────────────────────────────────────────
@tree.command(name="resultado", description="[Admin] Registra o resultado de uma partida")
@app_commands.describe(
    vencedor="Quem ganhou a partida (@jogador)",
    perdedor="Quem perdeu a partida (@jogador)"
)
async def cmd_resultado(
    interaction: discord.Interaction,
    vencedor: discord.Member,
    perdedor: discord.Member
):
    if not eh_admin(interaction):
        await interaction.response.send_message("❌ Apenas admins podem registrar resultados.", ephemeral=True)
        return

    dados = carregar_dados()

    g_v, pos_v, dados_v = encontrar_jogador(dados, vencedor.id)
    g_p, pos_p, dados_p = encontrar_jogador(dados, perdedor.id)

    if g_v is None:
        await interaction.response.send_message(f"❌ {vencedor.display_name} não está no torneio.", ephemeral=True)
        return
    if g_p is None:
        await interaction.response.send_message(f"❌ {perdedor.display_name} não está no torneio.", ephemeral=True)
        return

    # Atualiza estatísticas
    dados_v["vitorias"] = dados_v.get("vitorias", 0) + 1
    dados_v["sequencia"] = dados_v.get("sequencia", 0) + 1
    dados_p["derrotas"] = dados_p.get("derrotas", 0) + 1
    dados_p["sequencia"] = 0  # reset sequência do perdedor

    mensagens = []
    mensagens.append(f"✅ **{vencedor.display_name}** venceu **{perdedor.display_name}**!")

    seq_v = dados_v["sequencia"]

    # ── Lógica de subida de posição ──
    # Caso 1: mesma divisão — vencedor sobe uma posição (se estiver abaixo do perdedor)
    if g_v == g_p:
        lista = dados[str(g_v)]
        if pos_v > pos_p:
            # Troca de posição
            lista[pos_v], lista[pos_p] = lista[pos_p], lista[pos_v]
            nova_pos = pos_p + 1
            mensagens.append(f"📈 {vencedor.display_name} subiu para **{nova_pos}º lugar** no {GRUPOS[g_v]['nome']}!")
        else:
            mensagens.append(f"ℹ️ {vencedor.display_name} já está acima do perdedor — posições mantidas.")
    else:
        mensagens.append(f"ℹ️ Partida entre divisões — posições mantidas. Use /subir se aplicável.")

    # ── Aviso de sequência ──
    if seq_v == 3:
        mensagens.append(
            f"🔥🔥🔥 **{vencedor.display_name} tem 3 vitórias seguidas!** "
            f"Pode desafiar QUALQUER jogador do {GRUPOS[g_v]['nome']}!"
        )
    elif seq_v > 3:
        mensagens.append(f"🔥 **{vencedor.display_name}** está em chama! {seq_v} vitórias seguidas!")

    salvar_dados(dados)
    await atualizar_tabela_canal(dados)
    await interaction.response.send_message("\n".join(mensagens))


# ─────────────────────────────────────────────
#  /subir — admin confirma promoção de divisão
# ─────────────────────────────────────────────
@tree.command(name="subir", description="[Admin] Promove um jogador para a divisão acima")
@app_commands.describe(jogador="O jogador que vai subir de divisão (@jogador)")
async def cmd_subir(interaction: discord.Interaction, jogador: discord.Member):
    if not eh_admin(interaction):
        await interaction.response.send_message("❌ Apenas admins podem usar este comando.", ephemeral=True)
        return

    dados = carregar_dados()
    grupo, pos, dados_j = encontrar_jogador(dados, jogador.id)

    if grupo is None:
        await interaction.response.send_message(f"❌ {jogador.display_name} não está no torneio.", ephemeral=True)
        return

    if grupo == 0:
        await interaction.response.send_message(
            f"❌ {jogador.display_name} já está no grupo mais alto (Elite).", ephemeral=True
        )
        return

    novo_grupo = grupo - 1
    lista_atual = dados[str(grupo)]
    lista_nova = dados[str(novo_grupo)]
    max_novo = GRUPOS[novo_grupo]["max"]

    if len(lista_nova) >= max_novo:
        await interaction.response.send_message(
            f"❌ O {GRUPOS[novo_grupo]['nome']} está cheio ({max_novo}/{max_novo}). "
            f"Remova alguém antes de promover.", ephemeral=True
        )
        return

    # Remove da divisão atual e coloca no último lugar da divisão acima
    lista_atual.pop(pos)
    dados_j["sequencia"] = 0  # reset sequência ao subir
    lista_nova.append(dados_j)

    dados[str(grupo)] = lista_atual
    dados[str(novo_grupo)] = lista_nova
    salvar_dados(dados)
    await atualizar_tabela_canal(dados)

    pos_nova = len(lista_nova)
    await interaction.response.send_message(
        f"🎉 **{jogador.display_name}** subiu do **{GRUPOS[grupo]['nome']}** "
        f"para o **{GRUPOS[novo_grupo]['nome']}**!\n"
        f"Posição: **{pos_nova}º lugar** (último da nova divisão). Boa sorte! 💪"
    )


# ─────────────────────────────────────────────
#  /remover — admin remove jogador
# ─────────────────────────────────────────────
@tree.command(name="remover", description="[Admin] Remove um jogador do torneio")
@app_commands.describe(jogador="O jogador a ser removido (@jogador)")
async def cmd_remover(interaction: discord.Interaction, jogador: discord.Member):
    if not eh_admin(interaction):
        await interaction.response.send_message("❌ Apenas admins podem usar este comando.", ephemeral=True)
        return

    dados = carregar_dados()
    grupo, pos, _ = encontrar_jogador(dados, jogador.id)

    if grupo is None:
        await interaction.response.send_message(f"❌ {jogador.display_name} não está no torneio.", ephemeral=True)
        return

    dados[str(grupo)].pop(pos)
    salvar_dados(dados)
    await atualizar_tabela_canal(dados)

    await interaction.response.send_message(
        f"🗑️ **{jogador.display_name}** foi removido do **{GRUPOS[grupo]['nome']}**."
    )


# ─────────────────────────────────────────────
#  /tabela — mostra a tabela no chat
# ─────────────────────────────────────────────
@tree.command(name="tabela", description="Mostra a tabela atual do torneio")
async def cmd_tabela(interaction: discord.Interaction):
    dados = carregar_dados()
    conteudo = gerar_tabela(dados)
    # Discord tem limite de 2000 chars por mensagem
    if len(conteudo) > 1900:
        await interaction.response.send_message("📊 Tabela atualizada no canal fixado!", ephemeral=True)
    else:
        await interaction.response.send_message(conteudo)


# ─────────────────────────────────────────────
#  /perfil — mostra stats de um jogador
# ─────────────────────────────────────────────
@tree.command(name="perfil", description="Veja as estatísticas de um jogador")
@app_commands.describe(jogador="Deixe em branco para ver o seu próprio perfil")
async def cmd_perfil(interaction: discord.Interaction, jogador: discord.Member = None):
    alvo = jogador or interaction.user
    dados = carregar_dados()
    grupo, pos, dados_j = encontrar_jogador(dados, alvo.id)

    if grupo is None:
        await interaction.response.send_message(f"❌ {alvo.display_name} não está no torneio.", ephemeral=True)
        return

    v = dados_j.get("vitorias", 0)
    d = dados_j.get("derrotas", 0)
    seq = dados_j.get("sequencia", 0)
    total = v + d
    wr = round((v / total * 100)) if total > 0 else 0

    embed = discord.Embed(
        title=f"🎮 {dados_j['nome']}",
        color=0x5865F2
    )
    embed.add_field(name="Divisão", value=f"{GRUPOS[grupo]['emoji']} {GRUPOS[grupo]['nome']}", inline=True)
    embed.add_field(name="Posição", value=f"#{pos + 1}", inline=True)
    embed.add_field(name="Winrate", value=f"{wr}%", inline=True)
    embed.add_field(name="Vitórias", value=str(v), inline=True)
    embed.add_field(name="Derrotas", value=str(d), inline=True)
    embed.add_field(name="Sequência", value=f"{'🔥' * seq if seq > 0 else '-'} ({seq})", inline=True)

    if seq >= 3:
        embed.set_footer(text="🔥 Pode desafiar qualquer jogador da divisão!")

    await interaction.response.send_message(embed=embed)


# ─────────────────────────────────────────────
#  /ajuda — lista os comandos
# ─────────────────────────────────────────────
@tree.command(name="ajuda", description="Lista todos os comandos do bot")
async def cmd_ajuda(interaction: discord.Interaction):
    embed = discord.Embed(title="📋 Comandos do Ladder Bot", color=0x5865F2)

    embed.add_field(
        name="👤 Jogadores",
        value=(
            "`/entrar` — Entre no torneio (Grupo 4, último lugar)\n"
            "`/tabela` — Veja a tabela completa\n"
            "`/perfil [@jogador]` — Veja suas estatísticas\n"
        ),
        inline=False
    )
    embed.add_field(
        name="🛡️ Admins",
        value=(
            "`/adicionar @jogador grupo [posição]` — Adiciona jogador\n"
            "`/resultado @vencedor @perdedor` — Registra resultado\n"
            "`/subir @jogador` — Promove para divisão acima\n"
            "`/remover @jogador` — Remove do torneio\n"
        ),
        inline=False
    )
    embed.add_field(
        name="📜 Regras",
        value=(
            "• Desafie o jogador imediatamente acima de você\n"
            "• Ganhe → sobe uma posição\n"
            "• 3 vitórias seguidas → desafia qualquer um da divisão\n"
            "• Vencer o 1º → escolha ficar ou subir de divisão\n"
        ),
        inline=False
    )

    await interaction.response.send_message(embed=embed)


# ─────────────────────────────────────────────
#  EVENTOS
# ─────────────────────────────────────────────
@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ Bot online como {bot.user}")
    print(f"   Canal da tabela: {TABELA_CANAL_ID}")
    # Atualiza a tabela ao iniciar
    dados = carregar_dados()
    await atualizar_tabela_canal(dados)


bot.run(TOKEN)
