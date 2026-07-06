import os
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from cript_api import criptografar, descriptografar

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID", 0))
SEED = "e2025*"

class DataSavingBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print("Bot está online e comandos sincronizados.")

bot = DataSavingBot()

# Autocomplete functions
async def cofre_autocomplete(interaction: discord.Interaction, current: str):
    guild = bot.get_guild(GUILD_ID)
    if not guild: return []
    # Find forum channels starting with "datasaving-"
    forums = [c for c in guild.forums if c.name.startswith("datasaving-")]
    # Extract cofre name
    cofre_names = [c.name.replace("datasaving-", "") for c in forums]
    
    return [
        app_commands.Choice(name=nome, value=nome)
        for nome in cofre_names if current.lower() in nome.lower()
    ][:25]

async def title_autocomplete(interaction: discord.Interaction, current: str):
    cofre = interaction.namespace.cofre
    if not cofre:
        return []
    
    guild = bot.get_guild(GUILD_ID)
    if not guild: return []

    forum_name = f"datasaving-{cofre}".lower()
    forum = discord.utils.get(guild.forums, name=forum_name)
    if not forum:
        return []

    # Get threads inside the forum
    threads = forum.threads
    return [
        app_commands.Choice(name=t.name, value=t.name)
        for t in threads if current.lower() in t.name.lower()
    ][:25]

@bot.tree.command(name="save", description="Salva uma informação no banco de dados.")
@app_commands.describe(
    cofre="Nome do cofre (categoria do fórum)",
    title="Título da postagem no fórum",
    key="Chave secreta para recuperar a mensagem",
    menssagem="A mensagem a ser salva"
)
@app_commands.autocomplete(cofre=cofre_autocomplete, title=title_autocomplete)
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def save_command(interaction: discord.Interaction, cofre: str, title: str, key: str, menssagem: str):
    await interaction.response.defer(ephemeral=True)

    guild = bot.get_guild(GUILD_ID)
    if not guild:
        await interaction.followup.send("Erro: Servidor central não configurado ou bot não está no servidor.", ephemeral=True)
        return

    forum_name = f"datasaving-{cofre}".lower()
    
    # 1. Verifica se o canal Fórum existe, senão cria
    forum = discord.utils.get(guild.forums, name=forum_name)
    if not forum:
        try:
            forum = await guild.create_forum(name=forum_name)
        except Exception as e:
            await interaction.followup.send(f"Erro ao criar o fórum: {e}", ephemeral=True)
            return

    # 2. Verifica se a postagem {title} já existe (erro se sim)
    existing_thread = discord.utils.get(forum.threads, name=title)
    if not existing_thread:
        # Também verificar em threads arquivadas caso esteja arquivado
        archived_threads = []
        async for t in forum.archived_threads(limit=100):
            archived_threads.append(t)
        if discord.utils.get(archived_threads, name=title):
            existing_thread = True

    if existing_thread:
        await interaction.followup.send(f"Erro: O título '{title}' já existe no cofre '{cofre}'. Por favor, use um título diferente para não haver erros.", ephemeral=True)
        return

    # 3. Criar postagem no fórum
    try:
        # Usa a key do usuário + a seed predefinida como seed final
        seed_final = f"{key}{SEED}"
        msg_cripto = criptografar(menssagem, seed_final)
        
        conteudo_salvo = msg_cripto
        
        thread_with_message = await forum.create_thread(name=title, content=conteudo_salvo)
        await interaction.followup.send(f"Informação salva com sucesso no cofre '{cofre}', título '{title}'.", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"Erro ao salvar a mensagem: {e}", ephemeral=True)

@bot.tree.command(name="get", description="Recupera uma informação do banco de dados.")
@app_commands.describe(
    cofre="Nome do cofre",
    title="Título da postagem",
    key="Chave secreta"
)
@app_commands.autocomplete(cofre=cofre_autocomplete, title=title_autocomplete)
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def get_command(interaction: discord.Interaction, cofre: str, title: str, key: str):
    await interaction.response.defer(ephemeral=True)

    guild = bot.get_guild(GUILD_ID)
    if not guild:
        await interaction.followup.send("Erro: Servidor central não configurado ou bot não está no servidor.", ephemeral=True)
        return

    forum_name = f"datasaving-{cofre}".lower()
    
    forum = discord.utils.get(guild.forums, name=forum_name)
    if not forum:
        await interaction.followup.send(f"Cofre '{cofre}' não encontrado.", ephemeral=True)
        return

    thread = discord.utils.get(forum.threads, name=title)
    if not thread:
        archived_threads = []
        async for t in forum.archived_threads(limit=100):
            archived_threads.append(t)
        
        thread = discord.utils.get(archived_threads, name=title)
        if not thread:
            await interaction.followup.send(f"Título '{title}' não encontrado no cofre '{cofre}'.", ephemeral=True)
            return

    # 4. Ler a mensagem da thread e descriptografar cegamente
    seed_final = f"{key}{SEED}"
    
    found_msg = False
    async for message in thread.history(limit=50, oldest_first=True):
        content = message.content
        if content:
            try:
                msg_descripto = descriptografar(content, seed_final)
                await interaction.followup.send(f"**Mensagem recuperada:**\n(Se a chave estiver errada, o texto será ilegível)\n\n{msg_descripto}", ephemeral=True)
                found_msg = True
            except Exception as e:
                await interaction.followup.send(f"Erro ao descriptografar a mensagem: {e}", ephemeral=True)
            break

    if not found_msg:
        await interaction.followup.send("Mensagem não encontrada na postagem.", ephemeral=True)

if __name__ == "__main__":
    if not TOKEN or TOKEN == "seu_token_aqui":
        print("Por favor, configure o seu DISCORD_TOKEN no arquivo .env")
    else:
        bot.run(TOKEN)
