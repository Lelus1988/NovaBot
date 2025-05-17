import discord
from discord import app_commands
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True  # Falls du später Nachrichten verarbeiten willst

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot ist bereit als {bot.user}")
    try:
        synced = await bot.tree.sync()  # Synchronisiert Slash Commands mit Discord
        print(f"Synced {len(synced)} Commands")
    except Exception as e:
        print(f"Fehler beim Synchronisieren: {e}")

@bot.tree.command(name="join", description="Lass den Bot deinem Voice-Channel joinen")
async def join(interaction: discord.Interaction):
    if interaction.user.voice and interaction.user.voice.channel:
        channel = interaction.user.voice.channel
        # Verbinde mit dem Voice-Channel (oder bewege den Bot dorthin)
        if interaction.guild.voice_client is None:
            await channel.connect()
        else:
            await interaction.guild.voice_client.move_to(channel)

        await interaction.response.send_message(f"Ich bin dem Voice-Channel **{channel.name}** beigetreten!", ephemeral=True)
    else:
        await interaction.response.send_message("Du bist in keinem Voice-Channel!", ephemeral=True)

bot.run(os.getenv("DISCORD_BOT_TOKEN"))
