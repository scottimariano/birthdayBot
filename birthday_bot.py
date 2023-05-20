import os
import json
import discord
import time
import datetime
import asyncio
import messages
import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.oauth2 import service_account
from dotenv import load_dotenv
from discord.ext import tasks, commands


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
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', help_command=None, intents=intents)
# Maneja el evento de inicio de sesión del bot
@bot.event
async def on_ready():

    # Comprobar si el bot está conectado a algún servidor
    if not bot.guilds:
        print("Bot is not connected to any guilds.")

    else:

        for guild in bot.guilds:
            print(f'Logged in as {bot.user} in {guild.name}')
        
        if not mensajes.is_running():
            mensajes.start() #If the task is not already running, start it.
            print("mensajes task started")

timezone = datetime.timezone(datetime.timedelta(hours=-3))
scheduled_time = datetime.time(hour=9, minute=30, tzinfo=timezone)
# Maneja el envío de mensajes de cumpleaños
@tasks.loop(time=scheduled_time, reconnect=True)
async def mensajes():
    if bot.guilds:
        # Actualiza los datos de la hoja de cálculo
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range='Hoja 1!A2:B50').execute()
        values = result.get('values',[])
        
        for guild in bot.guilds:

            # Obtiene la lista de usuarios en el servidor de Discord
            # channel = discord.utils.get(guild.text_channels, name='🔷pigma-comunicacion')
            channel = discord.utils.get(guild.text_channels, name='general')
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
    else:
        print("El bot no está conectado a ningún servidor")

# Maneja el evento de unirse a un servidor
@bot.event
async def on_guild_join(guild_conected):
    print(f'Joined to {guild_conected.name}')
        
    # channel = discord.utils.get(guild_conected.text_channels, name='🔷pigma-comunicacion')
    channel = discord.utils.get(guild_conected.text_channels, name='general')
    
    async with channel.typing():
        await asyncio.sleep(10)
        
    message = '¡Soy Birthday Guru! :man_mage::birthday:\n Mi misión es que nadie se olvide de un cumpleaños! \nSi lo deseas, escribe "!help" para ver como puedo ayudarte.'
    await channel.send(message)
    
    if not mensajes.is_running():
        mensajes.start() #If the task is not already running, start it.
        print("mensajes task started")

# Maneja el evento de dejar un servidor
@bot.event
async def on_guild_remove(guild):
    print(f"Bot has been removed from {guild.name}")

    if not bot.guilds:
        print("Bot has been removed from all guilds")
        mensajes.stop()
        print("mensajes task stopped")

def get_registered_members(guild):
    # Obtener los datos de la hoja de cálculo
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range='Hoja 1!A3:A').execute()
    values = result.get('values', [])

    # Obtener la lista de nombres de usuarios registrados
    registered_members = [row[0] for row in values]

    # Filtrar los miembros registrados que son parte del canal actual
    members_in_channel = []
    for member_name in registered_members:
        member = discord.utils.get(guild.members, name=member_name)
        if member:
            members_in_channel.append(member_name)

    return members_in_channel


@bot.command()
async def help(ctx):

    async with ctx.typing():
        await asyncio.sleep(1)

    embed = discord.Embed(title='Birthday Guru', description='¡Hola! Soy Birthday Guru y puedo ayudar para que nadie se olvide de un cumpleaños.', color=discord.Color.blue())
    
    commands_list = [
        ('!hola', 'Ante todo los buenos modales.'),
        ('!cumple', 'Avisame cuando es tu cumple.'),
        ('!listado', 'Te cuento quienes ya confian en mi para recordar su cumple.'),
        ('!blue', 'Siempre es bueno estar informado.')
    ]
    
    commands_description = '\n'.join([f'`{command[0]}`: {command[1]}' for command in commands_list])
    
    embed.add_field(name='Comandos', value=commands_description, inline=False)
    
    await ctx.send(embed=embed)


@bot.command(name='hola', help='Ante todo la buena educación.')
async def hello(ctx):
    response = f"Hola {ctx.author.name} un honor saludarte! estoy a tu servicio. \nPara más información, puedes enviar un mesanje con el texto \"!help\" y te ayudaré"
    await ctx.reply(response)


@bot.command(name='cumple', help='Si lo deseas Birthday Guru recordará tu cumpleaños para avisar en el canal.')
async def add_birthday(ctx):
    
    async with ctx.typing():
        await asyncio.sleep(1)

    username = ctx.author.name
    registered_members = get_registered_members(ctx.guild)

    if username in registered_members:
        await ctx.reply('Ya sé cuando es tu cumple, tranquilo que no voy a olvidarlo.')
    else:
        response = f"Hola {ctx.author.name}, como estas?\n¿Cuándo es tu cumple? Por favor, responde con el formato dd/mm."
        await ctx.reply(response)
        
        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel
        
        try:
            message = await bot.wait_for('message', check=check, timeout=60)  # Espera la respuesta del usuario durante 60 segundos
            birthday = message.content
            
            # Validar el formato de fecha proporcionado
            try:
                birthday = datetime.datetime.strptime(birthday, '%d/%m')
            except ValueError:
                await ctx.reply('El formato de fecha debe ser dd/mm. Por favor, intenta nuevamente con "!cumple".')
                return
            
            # Convertir la fecha de cumpleaños a una cadena en formato 'dd/mm/yyyy'
            birthday_str = f"{birthday.day}/{birthday.month}"

            # Crear los datos para agregar a la hoja de cálculo
            data = [
                [ctx.author.name, birthday_str]
            ]
            
            # Obtener la última fila vacía en la hoja de cálculo
            result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range='Hoja 1!A:B').execute()
            values = result.get('values', [])
            last_row = len(values) + 1

            # Actualizar la hoja de cálculo con los nuevos datos
            result = sheet.values().update(spreadsheetId=SPREADSHEET_ID, range=f'Hoja 1!A{last_row}:B{last_row}', valueInputOption='USER_ENTERED', body={'values': data}).execute()
            
            # Actualizar la hoja de cálculo con los nuevos datos
            if result.get('updatedRows') == 1:
                await ctx.reply('Ok! trataré de acordarme... Cuando llegue el día avisaré en el canal.')
            else:
                await ctx.reply('Ocurrió un error al registrar tu cumpleaños. Por favor, intenta nuevamente con "!cumple".')
            
        except asyncio.TimeoutError:
            await ctx.reply('Tiempo de espera agotado. Por favor, intenta nuevamente con "!cumple".')

@bot.command(name='horario', hidden=True)
@commands.has_permissions(administrator=True)
async def config_time(ctx):
    await ctx.send("Por favor, ingresa la nueva hora para los saludos diarios en el formato HH:MM (hora:minuto).")

    def check(message):
        return message.author == ctx.author and message.channel == ctx.channel

    try:
        response = await bot.wait_for('message', timeout=60, check=check)

        # Obtener la nueva configuración de hora ingresada por el usuario
        new_time_str = response.content.strip()
        new_time = datetime.datetime.strptime(new_time_str, '%H:%M').time()

        global timezone
        new_time_with_timezone = new_time.replace(tzinfo=timezone)

        if mensajes and mensajes.is_running():
            # Detener la tarea 'mensajes'
            mensajes.change_interval(time=new_time_with_timezone)
            print("schedule updated to " + str(new_time))

        await ctx.send(f"La hora de los saludos diarios se ha actualizado correctamente. Nueva hora: {new_time_str}")
    except asyncio.TimeoutError:
        await ctx.send("No se ha recibido una respuesta. La configuración de hora no ha sido modificada.")
    except MissingPermissions:
        await ctx.send("¡Ups! Parece que no tienes los permisos de administrador para ejecutar este comando.")

@bot.command(name='blue', help='Siempre es bueno estar informado.')
async def blue_command(ctx):
    url = 'https://api.bluelytics.com.ar/v2/latest'
    
    try:
        response = requests.get(url)
        data = response.json()
        
        value_sell = data['blue']['value_sell']
        value_buy = data['blue']['value_buy']
        
        async with ctx.typing():
            await asyncio.sleep(1)

        await ctx.send(f"¡Ey! Te paso los precios tengo ahora. Me los pasó el amigo de un amigo:\n\n"
                       f":dollar: Venta:  ${value_sell}\n"
                       f":dollar: Compra: ${value_buy}\n"
                       f"¡Este precio es solo para vos...!")
        
    except requests.exceptions.RequestException as e:
        await ctx.send('Che, disculpá, pero no pude obtener los precios en este momento. ¡Intentá de nuevo más tarde!')


@bot.command(name='apagar', hidden=True)
@commands.has_permissions(administrator=True)
async def shutdown(ctx):
    # Mensaje de confirmación
    confirmation_message = "Confirmar apagado: ¿Estás seguro de que quieres apagarme? ¡No quiero irme! 😢"
    await ctx.send(confirmation_message)

    def check(message):
        return message.author == ctx.author and message.channel == ctx.channel

    try:
        response = await bot.wait_for('message', timeout=15, check=check)

        if response.content.lower() == 'sí' or response.content.lower() == 'si':
            await ctx.send("¡Adiós, mundo cruel! 😭")
            print("Apagando el bot local...")
            await bot.close()
        else:
            await ctx.send("¡Uf, casi me matas! ¡Gracias por salvarme! 😄")

    except asyncio.TimeoutError:
        await ctx.send("Demoraste demasiado. ¡Ya es demasiado tarde para apagarme! 😈")
    except commands.MissingPermissions:
        await ctx.send("¡Ups! Parece que no tienes los permisos de administrador para ejecutar este comando.")



@bot.command(name='listado', help='Muestra el listado de integrantes del canal ya registrados en la base de datos.')
async def show_registered_members(ctx):
    registered_members = get_registered_members(ctx.guild)

    if not registered_members:
        await ctx.reply('No hay integrantes registrados en la planilla.')
    else:
        member_list = "\n - ".join(registered_members)
        await ctx.reply(f'Integrantes registrados:\n - {member_list}')

# Inicia la conexión del bot
bot.run(os.getenv("DISCORD_BOT_TOKEN"))