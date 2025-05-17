import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

default_roles = [1372998922989207622, 1372993702456332371, 1372998326391406703,
                 1372998492024344728]


@bot.event
async def on_ready():
    print(f"Bot erfolgreich eingeloggt als {bot.user}")


@bot.event
async def on_member_join(member):

    if member.bot:
        return

    print(f"{member.name} ist beigetreten. Rollen werden zugewiesen ...")

    guild = member.guild

    for role_id in default_roles:
        role = guild.get_role(role_id)
        if role:
            try:
                await member.add_roles(role)
                print(f"Rolle {role.name} an {member.name} vergeben.")
            except discord.Forbidden:
                print(f"Keine Berechtigung, die Rolle {role.name} zu vergeben.")
            except discord.HTTPException as e:
                print(f"Ein Fehler bei der Vergabe der Rolle {role.name} ist aufgetreten: {e}")
        else:
            print(f"Rolle mit ID {role_id} existiert nicht.")

# Überprüfen, ob der Token verfügbar ist
token = os.getenv("DISCORD_BOT_TOKEN")
if not token:
    raise ValueError("Die Umgebungsvariable 'DISCORD_BOT_TOKEN' ist nicht gesetzt. Bitte setzen Sie diese, bevor Sie den Bot starten.")

bot.run(token)
