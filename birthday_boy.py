import os
import json
import discord
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.oauth2 import service_account
from dotenv import load_dotenv

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
GOOGLE_CREDENTIALS = json.loads(os.getenv("GOOGLE_CREDENTIALS"))

creds = None
creds = service_account.Credentials.from_service_account_info(info=GOOGLE_CREDENTIALS, scopes=SCOPES)


service = build('sheets', 'v4', credentials=creds)
sheet = service.spreadsheets()
result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range='Hoja 1!A2:B20').execute()
values = result.get('values',[])

# Configura el cliente de Discord
intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)

# Maneja el evento de inicio de sesión del bot
@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

    # Obtiene la lista de usuarios en el servidor de Discord
    guild = client.guilds[0] # cambia el índice según corresponda
    channel = guild.text_channels[0]
    members = guild.members

    # Itera sobre los datos y envía mensajes personalizados de cumpleaños a los usuarios correspondientes
    for row in values:
        name = row[0]
        date_str = row[1]
        date_obj = datetime.strptime(date_str, '%d/%m/%Y')

        # Verifica si es el cumpleaños del usuario hoy
        if date_obj.month == datetime.today().month and date_obj.day == datetime.today().day:
            user = discord.utils.find(lambda u: u.name == name, members)
            if user:
                message = f'¡Feliz cumpleaños, {user.mention}! 🎉🎂🎁'
                await channel.send(message)

    await client.close()

# Ejecuta el bot
client.run(os.getenv("DISCORD_BOT_TOKEN"))
