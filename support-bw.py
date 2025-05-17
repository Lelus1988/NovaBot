import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

TARGET_CHANNEL_ID = 1372986425061937202

@bot.event
async def on_ready():
    print(f"✅ Eingeloggt als {bot.user}")

    # Nachricht beim Start in Channel posten
    channel = bot.get_channel(TARGET_CHANNEL_ID)
    if channel:
        embed = discord.Embed(
            title="📢 Supporter Bewerbung",
            description=(
                "Hey, es ist so weit – **wir suchen DICH** für den Bereich **Kunden-Support / -Betreuung**! 🙌\n\n"
                "**Du solltest:**\n"
                "🔹 mindestens **14 Jahre alt** sein\n"
                "🔹 über **geistige Reife** verfügen\n"
                "🔹 bereits **Erfahrung im Support** gesammelt haben\n"
                "🔹 stets **höflich und respektvoll** sein\n\n"
                "✅ **Du erkennst dich wieder?**\n"
                "Dann **melde dich bei einem Admin** und **vereinbare ein Bewerbungsgespräch**!\n\n"
                "Wir freuen uns auf dich! 💬\n"
                "#TeamSupport"
            ),
            color=discord.Color.blue()
        )
        await channel.send(embed=embed)
    else:
        print("⚠️ Channel nicht gefunden. Prüfe die Channel-ID.")

# Starte den Bot (ersetze hier mit deinem echten Token)
bot.run(os.getenv("DISCORD_BOT_TOKEN"))
