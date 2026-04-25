import asyncio
import logging
import logging.handlers
import traceback

from telegram import Update
from telegram.ext import Application, ContextTypes

import database as db
from config import LOG_FILE, TELEGRAM_TOKEN
from handlers import admin_handlers, client_handlers


def setup_logging() -> None:
    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    console = logging.StreamHandler()
    console.setFormatter(fmt)
    root.addHandler(console)

    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(fmt)
    root.addHandler(file_handler)

    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("telegram").setLevel(logging.WARNING)
    logging.getLogger("handlers.client").setLevel(logging.DEBUG)
    logging.getLogger("handlers.admin").setLevel(logging.DEBUG)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger = logging.getLogger(__name__)
    logger.error("Excepción en handler:\n%s", "".join(traceback.format_exception(context.error)))
    if isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text(
            "⚠️ Ocurrió un error interno. Intenta de nuevo con /pedir."
        )


async def post_init(app: Application) -> None:
    await db.init_db()
    bot_info = await app.bot.get_me()
    logging.getLogger(__name__).info(
        "Bot iniciado: @%s (ID: %d)", bot_info.username, bot_info.id
    )


def build_app() -> Application:
    app = (
        Application.builder()
        .token(TELEGRAM_TOKEN)
        .post_init(post_init)
        .build()
    )
    client_handlers(app)
    admin_handlers(app)
    app.add_error_handler(error_handler)
    return app


def main() -> None:
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Iniciando OrderBot...")

    app = build_app()
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
