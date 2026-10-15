import asyncio
import logging
import math
import os

import gspread
from requests.exceptions import RequestException
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from expense import parse_expense

logger = logging.getLogger(__name__)


def _required_setting(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Falta configurar la variable de entorno {name}.")
    return value


def _allowed_user_ids() -> set[int]:
    raw_ids = os.environ.get("TELEGRAM_ALLOWED_USER_IDS", "").strip()
    if not raw_ids:
        return set()

    try:
        return {int(user_id.strip()) for user_id in raw_ids.split(",")}
    except ValueError as error:
        raise RuntimeError(
            "TELEGRAM_ALLOWED_USER_IDS debe ser una lista de IDs numéricos separados por comas."
        ) from error


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        await update.message.reply_text(
            "Envíame cada gasto como: monto descripción\n"
            "Por ejemplo: 12,50 café"
        )


async def add_expense(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    if message is None or message.text is None:
        return

    allowed_user_ids: set[int] = context.application.bot_data["allowed_user_ids"]
    user = update.effective_user
    if allowed_user_ids and (user is None or user.id not in allowed_user_ids):
        await message.reply_text("No tienes permiso para registrar gastos en este bot.")
        return

    try:
        expense = parse_expense(message.text)
    except ValueError as error:
        await message.reply_text(str(error))
        return

    amount = float(expense.amount)
    if not math.isfinite(amount):
        await message.reply_text("El monto es demasiado grande para guardarlo.")
        return

    worksheet: gspread.Worksheet = context.application.bot_data["worksheet"]
    try:
        await asyncio.to_thread(
            worksheet.append_row,
            [amount, expense.description],
            value_input_option="RAW",
        )
    except (gspread.exceptions.GSpreadException, RequestException, OSError):
        logger.exception("No se pudo guardar un gasto en Google Sheets.")
        await message.reply_text("No pude guardar el gasto. Inténtalo de nuevo más tarde.")
        return

    await message.reply_text(
        f"Registrado: {expense.amount} — {expense.description}"
    )


def build_application() -> Application:
    token = _required_setting("TELEGRAM_BOT_TOKEN")
    spreadsheet_id = _required_setting("GOOGLE_SPREADSHEET_ID")
    credentials_file = _required_setting("GOOGLE_SERVICE_ACCOUNT_FILE")
    worksheet_name = os.environ.get("GOOGLE_SHEETS_WORKSHEET", "Gastos").strip()
    if not worksheet_name:
        raise RuntimeError("GOOGLE_SHEETS_WORKSHEET no puede estar vacío.")

    client = gspread.service_account(filename=credentials_file)
    worksheet = client.open_by_key(spreadsheet_id).worksheet(worksheet_name)

    application = Application.builder().token(token).build()
    application.bot_data["worksheet"] = worksheet
    application.bot_data["allowed_user_ids"] = _allowed_user_ids()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, add_expense))
    return application


def main() -> None:
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        level=logging.INFO,
    )
    build_application().run_polling()


if __name__ == "__main__":
    main()
