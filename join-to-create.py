import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

# Lade die Umgebungsvariablen
load_dotenv()

intents = discord.Intents.default()
intents.voice_states = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Stelle sicher, dass du diese ID anpasst
JOIN_TO_CREATE_CHANNEL_ID = 1373003728747237396

# Dictionary zur Speicherung der User-VCs
user_channels = {}

@bot.event
async def on_ready():
    print(f"Bot ist online als {bot.user.name}")

@bot.event
async def on_voice_state_update(member, before, after):
    # Beitritt zum Join-to-Create Channel
    if after.channel and after.channel.id == JOIN_TO_CREATE_CHANNEL_ID:
        guild = member.guild
        category = after.channel.category

        # Erstelle einen neuen Channel für den User
        new_channel = await guild.create_voice_channel(
            name=f"{member.name}'s Channel",
            category=category,
            user_limit=5,
            overwrites={
                guild.default_role: discord.PermissionOverwrite(connect=True),
                member: discord.PermissionOverwrite(manage_channels=True)
            }
        )

        # Verschiebe den User in den neuen Channel
        await member.move_to(new_channel)

        # Speichern für spätere Löschung
        user_channels[member.id] = new_channel.id

    # Wenn ein Channel leer ist und er von uns erstellt wurde, löschen
    if before.channel and before.channel.id in user_channels.values():
        if len(before.channel.members) == 0:
            await before.channel.delete()
            # Entferne aus dem Tracking
            for uid, cid in list(user_channels.items()):
                if cid == before.channel.id:
                    del user_channels[uid]

# Starte den Bot
bot.run(os.getenv("DISCORD_BOT_TOKEN"))
