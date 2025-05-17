import discord
from discord.ext import commands
import random
import string
import time
from dotenv import load_dotenv
import os

# .env laden, falls nicht bereits implementiert (für sicheren Bot-Token)
load_dotenv()

# Intents erstellen
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.guild_messages = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# IDs und globale Variablen
SUPPORT_ROLE_ID = 1373021295318536262  # Rolle für Support-Mitglieder
SUPPORT_CATEGORY_ID = 1373244410661179484  # ID der Kategorie für Support-Tickets
APPLICATION_CATEGORY_ID = 1373244410661179485  # ID der Kategorie für Bewerbungen
LOG_CHANNEL_ID = 1373262569770455070  # ID des Log-Kanals

ticket_number = 1  # Startnummer für Tickets


def generate_ticket_id():
    """
    Erstellt eine zufällige Ticket-ID (z. B. #G713L48M).
    """
    return "#" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))


@bot.event
async def on_ready():
    """
    Event, das ausgelöst wird, wenn der Bot gestartet wird.
    """
    print(f"✅ Der Bot {bot.user} ist jetzt online!")


class TicketDropdown(discord.ui.Select):
    """
    Dropdown-Menü zur Auswahl des Ticket-Typs
    """

    def __init__(self):
        options = [
            discord.SelectOption(label="Support", description="Erstelle ein Support-Ticket", emoji="🎫"),
            discord.SelectOption(label="Teambewerbung", description="Bewerbe dich für das Team", emoji="📄")
        ]
        super().__init__(placeholder="Wähle dein Anliegen aus...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        """
        Callback-Funktion, wenn der Benutzer eine Option aus dem Dropdown-Menü auswählt.
        """
        global ticket_number
        ticket_number += 1
        ticket_id = generate_ticket_id()
        selection = self.values[0]  # Ausgewählte Option: "Support" oder "Teambewerbung"

        # Kanal finden oder Kategorie prüfen
        guild = interaction.guild
        if selection == "Support":
            category_id = SUPPORT_CATEGORY_ID
            title = f"Support Ticket #{ticket_number}"
            description = (f"Hallo, {interaction.user.mention}!\n\n"
                           "Bitte habe einen Moment Geduld. Unser Support-Team wird sich bald um dein Anliegen kümmern.")
            color = discord.Color.blue()
        elif selection == "Teambewerbung":
            category_id = APPLICATION_CATEGORY_ID
            title = f"Teambewerbung Ticket #{ticket_number}"
            description = (f"Hallo, {interaction.user.mention}!\n\n"
                           "Bitte schildere hier deine Bewerbung. Unser Team wird sich umgehend bei dir melden.")
            color = discord.Color.green()
        else:
            await interaction.response.send_message("Ungültige Auswahl", ephemeral=True)
            return

        # Kategorie- und Kanalberechtigungen prüfen
        category = guild.get_channel(category_id)
        if not category or category.type != discord.ChannelType.category:
            await interaction.response.send_message(
                "Die Kategorie für das Ticket konnte nicht gefunden werden. Bitte überprüfe die Einstellungen.",
                ephemeral=True
            )
            return

        # Kanal-Berechtigungen setzen
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(
                view_channel=True, send_messages=True, read_message_history=True
            ),
        }
        support_role = guild.get_role(SUPPORT_ROLE_ID)
        if support_role:
            overwrites[support_role] = discord.PermissionOverwrite(
                view_channel=True, send_messages=True, read_message_history=True
            )

        # Ticket-Kanal erstellen
        channel = await guild.create_text_channel(
            name=f"{selection.lower()}-{interaction.user.name.lower()}-{ticket_number}",
            category=category,
            overwrites=overwrites,
            reason=f"{selection} Ticket von {interaction.user}"
        )

        # Nachricht in Ticket senden
        embed = discord.Embed(title=title, description=description, color=color)
        await channel.send(embed=embed, view=CloseButtonView())

        # Log-Nachricht
        log_channel = guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            log_embed = discord.Embed(
                title="Neues Ticket erstellt",
                description=(
                    f"**Ticket-Typ:** {selection}\n"
                    f"**Ersteller:** {interaction.user.mention}\n"
                    f"**Ticket-ID:** {ticket_id}\n"
                    f"**Ticket-Nummer:** #{ticket_number}\n"
                    f"**Kanal:** {channel.mention}"
                ),
                color=discord.Color.orange()
            )
            await log_channel.send(embed=log_embed)

        # Bestätigung für Nutzer
        await interaction.response.send_message(
            f"Dein {selection}-Ticket wurde erstellt: {channel.mention}", ephemeral=True
        )


class TicketDropdownView(discord.ui.View):
    """
    Ansicht für das Dropdown-Menü
    """

    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketDropdown())


class CloseButtonView(discord.ui.View):
    """
    Ansicht für den Button, um ein Ticket zu schließen
    """

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Ticket schließen", style=discord.ButtonStyle.red, emoji="❌")
    async def close_ticket_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Schließt ein Ticket (nur Support-Team-Mitglieder oder Ersteller).
        """
        support_role = interaction.guild.get_role(SUPPORT_ROLE_ID)
        if support_role not in interaction.user.roles and interaction.channel.category_id not in [
            SUPPORT_CATEGORY_ID, APPLICATION_CATEGORY_ID
        ]:
            await interaction.response.send_message(
                "Du hast keine Berechtigung, dieses Ticket zu schließen.", ephemeral=True
            )
            return

        await interaction.response.send_message(
            "Das Ticket wird nun geschlossen. Danke für dein Anliegen!", ephemeral=True
        )
        await interaction.channel.delete(reason=f"Ticket geschlossen von {interaction.user}")


@bot.command()
async def ticket(ctx):
    """
    Befehl, um das Dropdown-Menü senden zu lassen.
    """
    view = TicketDropdownView()
    await ctx.send("Wähle bitte aus dem Dropdown-Menü, welches Ticket du erstellen möchtest:", view=view)


# Bot starten
bot.run(os.getenv("DISCORD_BOT_TOKEN"))
