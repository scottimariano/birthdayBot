import os
import json
import discord
import time
import datetime
import asyncio
import messages
import gspread
import requests
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from dotenv import load_dotenv
from discord.ext import tasks, commands


load_dotenv()


SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
GOOGLE_CREDENTIALS = json.loads(os.getenv("GOOGLE_CREDENTIALS"))
creds = None
creds = service_account.Credentials.from_service_account_info(info=GOOGLE_CREDENTIALS, scopes=SCOPES)
gc = gspread.authorize(creds)
sheet = gc.open("Cumpleaños")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', help_command=None, intents=intents)

# Maneja el evento de inicio de sesión del bot
@bot.event
async def on_ready():

    if not bot.guilds:
        print("Bot is not connected to any guilds.")

    else:

        for guild in bot.guilds:
            print(f'Logged in as {bot.user} in {guild.name}')
        
        if not mensajes.is_running():
            mensajes.start() #If the task is not already running, start it.
            print("mensajes task started")


# Maneja el evento de unirse a un servidor
@bot.event
async def on_guild_join(guild_conected):
    print(f'Joined to {guild_conected.name}')

    set_or_create_worksheet(guild_conected.name, guild_conected.id)

    channel = channel = guild_conected.text_channels[0]
    
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


timezone = datetime.timezone(datetime.timedelta(hours=-3))
scheduled_time = datetime.time(hour=12, minute=41, tzinfo=timezone)
# Maneja el envío de mensajes de cumpleaños
@tasks.loop(time=scheduled_time, reconnect=True)
async def mensajes():
    if bot.guilds:
        
        for guild in bot.guilds:

            worksheet = set_or_create_worksheet(guild.name, guild.id)
            channel = discord.utils.get(guild.text_channels, name=worksheet.acell('E1').value)
            if not channel:
                channel = guild.text_channels[0]

            members = guild.members

            values = worksheet.get("A2:B")

            for row in values:
                name = row[0]
                date_str = row[1]
                date_obj = datetime.datetime.strptime(date_str, '%d/%m/%Y')

                if date_obj.month == datetime.datetime.today().month and date_obj.day == datetime.datetime.today().day:
                    user = discord.utils.find(lambda u: u.name == name, members)
                    if user:
                        message = messages.generate_greeting(user)
                        await channel.send(message + "@everyone")
                        print(f'Messaged Sended to {user.name} in {guild.name}')
    else:
        print("El bot no está conectado a ningún servidor")


# Return worksheet for the_channel
def set_or_create_worksheet(guild_name, guild_id):
    try:
        worksheet = sheet.worksheet(f"{guild_name} {guild_id}")
    except gspread.exceptions.WorksheetNotFound:
        worksheet = sheet.worksheet("Base")
        worksheet.duplicate(new_sheet_name=f"{guild_name} {guild_id}")
        worksheet = sheet.worksheet(f"{guild_name} {guild_id}")
    
    return worksheet


@bot.command()
async def help(ctx):

    async with ctx.typing():
        await asyncio.sleep(1)

    embed = discord.Embed(title='Birthday Guru', description='¡Hola! Soy Birthday Guru y puedo ayudar para que nadie se olvide de un cumpleaños.', color=discord.Color.blue())
    
    commands_list = [
        ('!hola', 'Ante todo los buenos modales.'),
        ('!cumple', 'Avisame cuando es tu cumple. y yo me encargo que nadie se olvide.'),
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
    
    worksheet = set_or_create_worksheet(ctx.guild.name, ctx.guild.id)

    registered_members = worksheet.col_values(1)

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
            
            try:
                # Obtener la última fila vacía en la hoja de cálculo
                next_row = len(worksheet.col_values(1)) + 1

                # Actualizar la hoja de cálculo con los nuevos datos
                worksheet.update_cell(next_row, 1, ctx.author.name)
                worksheet.update_cell(next_row, 2, birthday_str)

                await ctx.reply('Ok! trataré de acordarme... Cuando llegue el día avisaré en el canal.')
            except gspread.exceptions.APIError(response):
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

        await ctx.send(f"La hora de los saludos de cumpleaños se ha actualizado correctamente. Nueva hora: {new_time_str}")
    except asyncio.TimeoutError:
        await ctx.send("No se ha recibido una respuesta. La configuración de hora no ha sido modificada.")
    except MissingPermissions:
        await ctx.send("¡Ups! Parece que no tienes los permisos de administrador para ejecutar este comando.")


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


@bot.command(name='canal', hidden=True)
@commands.has_permissions(administrator=True)
async def canal(ctx):

    worksheet = set_or_create_worksheet(ctx.guild.name, ctx.guild.id)

    text_channels = ctx.guild.text_channels

    channel_names = [channel.name for channel in text_channels]

    message = "Elige un canal para enviar los mensajes de cumpleaños, seleccionando el número correspondiente:\n\n"
    for i, name in enumerate(channel_names):
        message += f"{i+1}. {name}\n"

    await ctx.send(message)

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    while True:
        try:

            user_response = await bot.wait_for('message', check=check, timeout=30)

            channel_index = int(user_response.content) - 1

            selected_channel = text_channels[channel_index]

            worksheet.update('E1', selected_channel.name)
            print(f"Channel updated in {ctx.guild.name}: {selected_channel.name}")

            await ctx.send(f"De ahora en adelante, los mensajes de cumpleaños los enviaré en el canal {selected_channel.mention}.")
            break

        except (ValueError, IndexError):
            await ctx.send("Opción inválida. Por favor, elegí un número del listado")
        
        except asyncio.TimeoutError:
            await ctx.send("Tiempo de espera agotado. Inicia nuevamente con !canal")
            break


@bot.command(name='listado', help='Muestra el listado de integrantes del canal ya registrados en la base de datos.')
async def show_registered_members(ctx):

    worksheet = set_or_create_worksheet(ctx.guild.name, ctx.guild.id)
    registered_members = worksheet.get("A2:A")

    if not registered_members:
        await ctx.reply('No hay integrantes registrados en la planilla de cumpleaños.\nPuedes incluirte escribiendo "!cumple"')
    else:
        message = "Integrantes registrados:\n"
        for item in registered_members:
            message += "- " + item[0] + "\n"
        await ctx.reply(message)


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


# Inicia la conexión del bot
bot.run(os.getenv("DISCORD_BOT_TOKEN"))