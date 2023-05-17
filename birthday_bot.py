import os
import json
import discord
import schedule
import time
import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.oauth2 import service_account
from dotenv import load_dotenv
from discord.ext import tasks, commands
import messages


load_dotenv()



SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
GOOGLE_CREDENTIALS = json.loads(os.getenv("GOOGLE_CREDENTIALS"))
creds = None
creds = service_account.Credentials.from_service_account_info(info=GOOGLE_CREDENTIALS, scopes=SCOPES)
service = build('sheets', 'v4', credentials=creds)
sheet = service.spreadsheets()

# Configura el cliente de Discord
intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)
guild = None

# Maneja el evento de inicio de sesión del bot
@client.event
async def on_ready():
    
    # Comprobar si el bot está conectado a algún servidor
    if not client.guilds:
        print("Bot is not connected to any guilds.")

    else:
        global guild
        guild = client.guilds[0] # cambia el índice según corresponda
        print(f'Logged in as {client.user} in {guild.name}')
        if not mensajes.is_running():
            mensajes.start() #If the task is not already running, start it.
            print("mensajes task started")

goodNightTime = datetime.time(hour=18, minute=52, second=30)
# Maneja el envío de mensajes de cumpleaños
@tasks.loop(time=goodNightTime)
async def mensajes():
    if client.guilds:
        global guild
        if guild is None:
            return

        # Actualiza los datos de la hoja de cálculo
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range='Hoja 1!A2:B50').execute()
        values = result.get('values',[])

        # Obtiene la lista de usuarios en el servidor de Discord
        channel = discord.utils.get(guild.text_channels, name='🔷pigma-comunicacion')
        members = guild.members

        # Itera sobre los datos y envía mensajes personalizados de cumpleaños a los usuarios correspondientes
        for row in values:
            name = row[0]
            date_str = row[1]
            date_obj = datetime.datetime.strptime(date_str, '%d/%m/%Y')

            # Verifica si es el cumpleaños del usuario hoy
            if date_obj.month == datetime.datetime.today().month and date_obj.day == datetime.datetime.today().day:
                user = discord.utils.find(lambda u: u.name == name, members)
                if user:
                    message = messages.generate_greeting(user)
                    await channel.send(message)
                    print('Messaged Sended')

# Maneja el evento de unirse a un servidor
@client.event
async def on_guild_join(guild_conected):
    print(f'Joined to {guild_conected.name}')
    channel = guild_conected.text_channels[0]
    message = '¡Soy Bot birthday! 🎉🎂🎁'
    await channel.send(message)
    global guild
    guild = guild_conected
    if not mensajes.is_running():
        mensajes.start() #If the task is not already running, start it.
        print("mensajes task started")

# Maneja el evento de dejar un servidor
@client.event
async def on_guild_remove(guild):
    print(f'Bot has been removed from {guild.name}')
    mensajes.stop()
    print("mensajes task stopped")


# Inicia la conexión del bot
client.run(os.getenv("DISCORD_BOT_TOKEN"))