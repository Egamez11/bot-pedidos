import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN: str = os.environ["TELEGRAM_TOKEN"]
ADMIN_ID: int = int(os.environ["ADMIN_ID"])
DATABASE_URL: str = "orderbot.db"
LOG_FILE: str = "orderbot.log"

ORDER_STATUSES: list[str] = [
    "pendiente",
    "confirmado",
    "en preparación",
    "enviado",
    "entregado",
]

STATUS_NEXT: dict[str, str | None] = {
    "pendiente": "confirmado",
    "confirmado": "en preparación",
    "en preparación": "enviado",
    "enviado": "entregado",
    "entregado": None,
}

STATUS_EMOJI: dict[str, str] = {
    "pendiente": "🕐",
    "confirmado": "✅",
    "en preparación": "👨‍🍳",
    "enviado": "🚀",
    "entregado": "🎉",
}
