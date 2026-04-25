from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup

from models import Product


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    buttons = [
        ["🛍️ Catálogo", "📦 Hacer pedido"],
        ["📋 Mis pedidos"],
    ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)


def catalog_keyboard(products: list[Product]) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(f"{p.name} — ${p.price:.0f} MXN", callback_data=f"product:{p.id}")]
        for p in products
    ]
    buttons.append([InlineKeyboardButton("❌ Cancelar", callback_data="cancel")])
    return InlineKeyboardMarkup(buttons)


def confirm_order_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton("✅ Confirmar", callback_data="confirm_order"),
            InlineKeyboardButton("❌ Cancelar", callback_data="cancel"),
        ]
    ]
    return InlineKeyboardMarkup(buttons)


def admin_panel_keyboard() -> ReplyKeyboardMarkup:
    buttons = [
        ["📋 Pedidos activos", "📊 Estadísticas"],
    ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)


def order_action_keyboard(order_id: int, next_status: str | None) -> InlineKeyboardMarkup:
    buttons = []
    if next_status:
        buttons.append(
            InlineKeyboardButton(
                f"➡️ Avanzar a '{next_status}'",
                callback_data=f"advance:{order_id}",
            )
        )
    return InlineKeyboardMarkup([[btn] for btn in buttons]) if buttons else InlineKeyboardMarkup([])
