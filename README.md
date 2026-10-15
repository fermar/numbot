# numbot

Bot de Telegram en Python para registrar gastos en Google Sheets. Envía un
mensaje con el formato `monto descripción`, por ejemplo `12,50 café`. El monto
y la descripción se guardan en las columnas A y B, respectivamente.

## Configuración

1. Crea un bot con [@BotFather](https://t.me/BotFather) y guarda su token.
2. En Google Cloud, habilita la API de Google Sheets y crea una cuenta de
   servicio. Descarga su archivo JSON de credenciales y compártelo con permisos
   de **Editor** en el spreadsheet donde guardarás los gastos.
3. Crea una pestaña llamada `Gastos` en ese spreadsheet (o configura otro nombre
   con `GOOGLE_SHEETS_WORKSHEET`) y copia su ID desde la URL.
4. Instala las dependencias y configura las variables de entorno:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt

   export TELEGRAM_BOT_TOKEN="token-del-bot"
   export GOOGLE_SPREADSHEET_ID="id-del-spreadsheet"
   export GOOGLE_SERVICE_ACCOUNT_FILE="/ruta/a/service-account.json"
   # Recomendado para que solo tu usuario pueda registrar gastos:
   export TELEGRAM_ALLOWED_USER_IDS="123456789"
   python bot.py
   ```

   Puedes obtener tu ID numérico de Telegram con un bot de consulta de IDs.
   Para permitir varios usuarios, sepáralos por comas. Si no se configura
   `TELEGRAM_ALLOWED_USER_IDS`, el bot acepta mensajes de cualquier usuario que
   pueda encontrarlo.

## Formato de mensajes

- `12,50 café con leche`
- `8.75 transporte`
- `€15 compra del mercado`

El monto debe ser positivo y tener como máximo dos decimales. Los mensajes que
no tengan el formato correcto reciben una indicación de uso; los gastos válidos
se añaden al final de la pestaña.

## Pruebas

```bash
python -m unittest discover -s tests
```
