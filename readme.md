# Birthday Guru - Discord Bot

Birthday Guru es un bot de Discord desarrollado en Python que te ayuda a recordar los cumpleaños de los miembros de tu servidor. El bot se conecta a una hoja de cálculo de Google para almacenar y administrar la información de los cumpleaños.

## Funcionalidades

- El bot puede enviar mensajes automáticos de cumpleaños en el canal designado de tu servidor de Discord.
- Los mensajes de cumpleaños se envían diariamente a una hora programada.
- Los usuarios pueden registrar su cumpleaños usando el comando `!cumple`.
- El bot mantiene un registro de los usuarios que han registrado su cumpleaños.

## Requisitos previos

Antes de ejecutar el bot, asegúrate de tener lo siguiente:

- Python 3.7 o superior instalado en tu máquina.
- Credenciales de Google API con acceso a Google Sheets y Google Drive.
- Un token de bot de Discord y los permisos necesarios para agregarlo a tu servidor de Discord.

## Configuración

1. Clona este repositorio en tu máquina local.
2. Instala las dependencias necesarias ejecutando el siguiente comando:

```bash
pip install -r requirements.txt
```


3. Crea un archivo .env en el directorio raíz del proyecto y agrega las siguientes variables de entorno:
```bash
DISCORD_BOT_TOKEN=your_discord_bot_token
SPREADSHEET_ID=your_google_spreadsheet_id
GOOGLE_CREDENTIALS=your_google_credentials_json
```

Una vez que hayas completado estos pasos, estarás listo para ejecutar el bot y comenzar a usarlo en tu servidor de Discord.


