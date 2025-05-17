import discord
from discord.ext import commands, tasks
import datetime
import random
import asyncio
import atexit
import os
import sys
from dotenv import load_dotenv

# .env laden
load_dotenv()

# Discord-Token abrufen
discord_token = os.getenv("DISCORD_BOT_TOKEN")
if not discord_token:
    print("❌ Fehler: Umgebungsvariable 'DISCORD_BOT_TOKEN' nicht gesetzt oder leer.")
    sys.exit(1)


CHANNEL_ID = 1372988650010185808
STATUS_MESSAGE_ID_FILE = "status_message_id.txt"

# Bot-Setup
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Status-System
status_systems_online = {
    "NovaBot": {"ping": 123, "uptime": "99.99%"},
    "Discord API": {"ping": 27, "uptime": "100.00%"},
    "Datenbank": {"ping": 45, "uptime": "99.90%"},
    "Moderation": {"ping": 70, "uptime": "99.95%"},
}

status_systems_offline = {
    name: {"ping": "Offline", "uptime": "0%"}
    for name in status_systems_online
}



# Event: Ein neues Mitglied tritt bei
@bot.event
async def on_member_join(member):
    await assign_roles(member)


# Hilfsfunktion: Statusnachricht formatieren
def format_status_line(name, ping, uptime, online=True):
    circle = "🟢" if online else "🔴"
    return f"{circle} **{name}**\nPing: `{ping}`\nUptime: `{uptime}`"


# Hilfsfunktion: Statusnachricht aktualisieren
async def update_status_message(message, online=True):
    systems = status_systems_online if online else status_systems_offline

    if online:
        for key in systems.keys():
            systems[key]["ping"] = random.randint(10, 200)

    embed = discord.Embed(
        title="NovaBot - Status",
        description="\n**Alle Informationen werden von NovaBot verwaltet.**\n\n",
        color=discord.Color.green() if online else discord.Color.red(),
    )

    for name, data in systems.items():
        embed.add_field(
            name="\u200b", value=format_status_line(name, data["ping"], data["uptime"], online), inline=True
        )

    embed.set_footer(
        text=f"Last updated | {datetime.datetime.now(datetime.timezone.utc).strftime('%d.%m.%Y %H:%M:%S UTC')}")
    await message.edit(embed=embed)


# Event: Bot ist bereit
@bot.event
async def on_ready():
    print(f"✅ NovaBot ist online: {bot.user}")
    await bot.change_presence(activity=discord.Game(name="NovaBot"))
    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        print("❌ Kanal nicht gefunden!")
        return

    message = None
    try:
        with open(STATUS_MESSAGE_ID_FILE, "r") as f:
            message_id = int(f.read())
            message = await channel.fetch_message(message_id)
    except Exception: pass

    if message is None:
        message = await channel.send(embed=discord.Embed(title="Starte Status..."))
        with open(STATUS_MESSAGE_ID_FILE, "w") as f:
            f.write(str(message.id))
        print("✅ Neue Statusnachricht gesendet.")

    await update_status_message(message, online=True)
    update_status_message_task.start(message)


# Loop: Statusnachricht regelmäßig aktualisieren
@tasks.loop(seconds=15)
async def update_status_message_task(message):
    await update_status_message(message, online=True)


# Event: Bot wird getrennt
@bot.event
async def on_disconnect():
    print("⚠️ NovaBot disconnected! Setze Status auf offline ...")

    async def offline_status():
        channel = bot.get_channel(CHANNEL_ID)
        if channel is None:
            return
        try:
            with open(STATUS_MESSAGE_ID_FILE, "r") as f:
                message_id = int(f.read())
                message = await channel.fetch_message(message_id)
                await update_status_message(message, online=False)
                print("✅ Status auf offline gesetzt.")
        except Exception as e:
            print(f"Fehler beim Setzen des Offline-Status: {e}")

    bot.loop.create_task(offline_status())


# Fehlerbehandlung beim Beenden
def on_exit():
    async def offline():
        await bot.wait_until_ready()
        channel = bot.get_channel(CHANNEL_ID)
        if channel is None:
            return
        try:
            with open(STATUS_MESSAGE_ID_FILE, "r") as f:
                message_id = int(f.read())
                message = await channel.fetch_message(message_id)
                await update_status_message(message, online=False)
                print("✅ Status beim Herunterfahren auf offline gesetzt.")
        except Exception as e:
            print(f"Fehler beim Setzen des Offline-Status beim Herunterfahren: {e}")

    asyncio.run_coroutine_threadsafe(offline(), bot.loop)


atexit.register(on_exit)

# Bot starten
bot.run(os.getenv("DISCORD_BOT_TOKEN"))
