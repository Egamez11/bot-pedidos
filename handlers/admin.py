import logging

from telegram import Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

import database as db
from config import ADMIN_ID, STATUS_EMOJI, STATUS_NEXT
from utils import admin_panel_keyboard, order_action_keyboard

logger = logging.getLogger(__name__)


def _is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


async def _require_admin(update: Update) -> bool:
    if not _is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ No tienes permisos para usar este comando.")
        return False
    return True


async def cmd_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _require_admin(update):
        return
    await update.message.reply_text(
        "🔧 *Panel de Administración — OrderBot*\n\n"
        "Selecciona una opción del menú:",
        parse_mode="Markdown",
        reply_markup=admin_panel_keyboard(),
    )


async def cmd_pedidos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _require_admin(update):
        return

    orders = await db.get_active_orders()
    if not orders:
        await update.message.reply_text("✅ No hay pedidos activos en este momento.")
        return

    await update.message.reply_text(
        f"📋 *Pedidos activos ({len(orders)})*", parse_mode="Markdown"
    )

    for order in orders:
        emoji = STATUS_EMOJI.get(order.status, "❓")
        next_status = STATUS_NEXT.get(order.status)
        text = (
            f"*Pedido #{order.id}*\n"
            f"👤 {order.client_name}\n"
            f"🍔 {order.product} x{order.quantity}\n"
            f"{emoji} Estado: _{order.status}_\n"
            f"🕐 {order.created_at.strftime('%d/%m/%Y %H:%M')}"
        )
        await update.message.reply_text(
            text,
            parse_mode="Markdown",
            reply_markup=order_action_keyboard(order.id, next_status),
        )


async def cmd_estadisticas(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _require_admin(update):
        return

    stats = await db.get_statistics()
    by_status_lines = "\n".join(
        f"  {STATUS_EMOJI.get(s, '❓')} {s}: *{q}*"
        for s, q in stats["by_status"].items()
    ) or "  Sin datos"

    top_name, top_qty = stats["top_product"]
    text = (
        "📊 *Estadísticas de OrderBot*\n\n"
        f"📅 Pedidos hoy: *{stats['today']}*\n"
        f"📆 Pedidos esta semana: *{stats['week']}*\n\n"
        f"*Por estado:*\n{by_status_lines}\n\n"
        f"🏆 Producto más pedido: *{top_name}* ({top_qty} pedidos)"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def handle_advance_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if not _is_admin(update.effective_user.id):
        await query.answer("⛔ Sin permisos.", show_alert=True)
        return

    order_id = int(query.data.split(":")[1])
    order = await db.get_order_by_id(order_id)

    if not order:
        await query.edit_message_text("❌ Pedido no encontrado.")
        return

    next_status = STATUS_NEXT.get(order.status)
    if not next_status:
        await query.answer("Este pedido ya está en el estado final.", show_alert=True)
        return

    await db.update_order_status(order_id, next_status)
    emoji = STATUS_EMOJI.get(next_status, "❓")

    await query.edit_message_text(
        f"✅ *Pedido #{order_id}* actualizado a {emoji} *{next_status}*",
        parse_mode="Markdown",
    )

    await _notify_client_status_update(context, order, next_status, emoji)
    logger.info("Admin actualizó pedido #%d → '%s'.", order_id, next_status)


async def _notify_client_status_update(
    context: ContextTypes.DEFAULT_TYPE,
    order,
    new_status: str,
    emoji: str,
) -> None:
    message = (
        f"🔔 *Actualización de tu pedido #{order.id}*\n\n"
        f"🍔 {order.product} x{order.quantity}\n"
        f"Nuevo estado: {emoji} *{new_status}*\n\n"
        "Usa /mispedidos para ver todos tus pedidos."
    )
    try:
        await context.bot.send_message(order.client_id, message, parse_mode="Markdown")
    except Exception as exc:
        logger.warning("No se pudo notificar al cliente %d: %s", order.client_id, exc)


async def handle_admin_menu_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    if text == "📋 Pedidos activos":
        await cmd_pedidos(update, context)
    elif text == "📊 Estadísticas":
        await cmd_estadisticas(update, context)


def admin_handlers(app: Application) -> None:
    app.add_handler(CommandHandler("admin", cmd_admin))
    app.add_handler(CommandHandler("pedidos", cmd_pedidos))
    app.add_handler(CommandHandler("estadisticas", cmd_estadisticas))
    app.add_handler(CallbackQueryHandler(handle_advance_order, pattern=r"^advance:\d+$"))
    app.add_handler(
        MessageHandler(
            filters.Regex("^(📋 Pedidos activos|📊 Estadísticas)$"),
            handle_admin_menu_buttons,
        )
    )
