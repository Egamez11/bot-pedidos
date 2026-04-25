import logging

from telegram import Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

import database as db
from config import ADMIN_ID, STATUS_EMOJI
from utils import catalog_keyboard, confirm_order_keyboard, main_menu_keyboard

logger = logging.getLogger(__name__)

# ConversationHandler states
SELECT_PRODUCT, ENTER_QUANTITY, CONFIRM_ORDER = range(3)

CONVERSATION_TIMEOUT = 300  # 5 minutos


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_text(
        f"👋 ¡Hola, *{user.first_name}*! Bienvenido a *OrderBot* 🍔\n\n"
        "Soy tu asistente de pedidos. Usa el menú para empezar.",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard(),
    )


async def cmd_catalogo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    products = await db.get_available_products()
    if not products:
        await update.message.reply_text("😔 No hay productos disponibles en este momento.")
        return

    lines = ["🍔 *Catálogo de productos*\n"]
    lines.extend(p.to_catalog_line() for p in products)
    await update.message.reply_text("\n\n".join(lines), parse_mode="Markdown")


async def cmd_mispedidos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    orders = await db.get_orders_by_client(user.id)

    if not orders:
        await update.message.reply_text("📭 Aún no tienes pedidos registrados.")
        return

    lines = ["📋 *Tus pedidos*\n"]
    for order in orders:
        emoji = STATUS_EMOJI.get(order.status, "❓")
        lines.append(
            f"*Pedido #{order.id}* — {order.product} x{order.quantity}\n"
            f"  {emoji} Estado: _{order.status}_\n"
            f"  🕐 {order.created_at.strftime('%d/%m/%Y %H:%M')}"
        )
    await update.message.reply_text("\n\n".join(lines), parse_mode="Markdown")


# --- ConversationHandler para /pedir ---

async def cmd_pedir(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    logger.debug("cmd_pedir ejecutado por usuario %d (%s)", user.id, user.first_name)
    products = await db.get_available_products()
    if not products:
        await update.message.reply_text("😔 No hay productos disponibles en este momento.")
        return ConversationHandler.END

    await update.message.reply_text(
        "🛒 *Nuevo pedido*\n\nSelecciona un producto:",
        parse_mode="Markdown",
        reply_markup=catalog_keyboard(products),
    )
    context.user_data["available_products"] = {p.id: p for p in products}
    return SELECT_PRODUCT


async def handle_product_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    if query.data == "cancel":
        await query.edit_message_text("❌ Pedido cancelado.")
        return ConversationHandler.END

    product_id = int(query.data.split(":")[1])
    products = context.user_data.get("available_products", {})
    product = products.get(product_id)

    if not product:
        await query.edit_message_text("❌ Producto no encontrado. Intenta de nuevo con /pedir.")
        return ConversationHandler.END

    context.user_data["selected_product"] = product
    await query.edit_message_text(
        f"✅ Seleccionaste: *{product.name}* — {product.format_price()}\n\n"
        "¿Cuántas unidades deseas? (Ingresa un número entre 1 y 20)",
        parse_mode="Markdown",
    )
    return ENTER_QUANTITY


async def handle_quantity_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()

    if not text.isdigit() or not (1 <= int(text) <= 20):
        await update.message.reply_text(
            "⚠️ Por favor ingresa un número válido entre *1* y *20*.",
            parse_mode="Markdown",
        )
        return ENTER_QUANTITY

    quantity = int(text)
    product = context.user_data["selected_product"]
    total = product.price * quantity

    context.user_data["quantity"] = quantity

    summary = (
        f"📋 *Resumen de tu pedido*\n\n"
        f"🍔 Producto: *{product.name}*\n"
        f"🔢 Cantidad: *{quantity}*\n"
        f"💰 Total: *${total:.0f} MXN*\n\n"
        "¿Confirmas tu pedido?"
    )
    await update.message.reply_text(
        summary,
        parse_mode="Markdown",
        reply_markup=confirm_order_keyboard(),
    )
    return CONFIRM_ORDER


async def handle_order_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    if query.data == "cancel":
        await query.edit_message_text("❌ Pedido cancelado.")
        return ConversationHandler.END

    user = update.effective_user
    product = context.user_data["selected_product"]
    quantity = context.user_data["quantity"]
    client_name = user.full_name

    order_id = await db.create_order(user.id, client_name, product.name, quantity)

    await query.edit_message_text(
        f"🎉 *¡Pedido #{order_id} recibido!*\n\n"
        f"🍔 {product.name} x{quantity}\n\n"
        "Te notificaremos cuando cambie el estado. Usa /mispedidos para ver tu historial.",
        parse_mode="Markdown",
    )

    await _notify_admin_new_order(context, order_id, client_name, user.id, product.name, quantity)
    logger.info("Pedido #%d creado por usuario %d (%s).", order_id, user.id, client_name)

    context.user_data.clear()
    return ConversationHandler.END


async def _notify_admin_new_order(
    context: ContextTypes.DEFAULT_TYPE,
    order_id: int,
    client_name: str,
    client_id: int,
    product: str,
    quantity: int,
) -> None:
    message = (
        f"🔔 *Nuevo pedido #{order_id}*\n\n"
        f"👤 Cliente: {client_name} (ID: `{client_id}`)\n"
        f"🍔 Producto: {product}\n"
        f"🔢 Cantidad: {quantity}\n\n"
        "Usa /pedidos para gestionar los pedidos activos."
    )
    try:
        await context.bot.send_message(ADMIN_ID, message, parse_mode="Markdown")
    except Exception as exc:
        logger.warning("No se pudo notificar al admin: %s", exc)


async def handle_timeout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message:
        await update.message.reply_text(
            "⏰ El pedido expiró por inactividad. Usa /pedir para comenzar de nuevo.",
        )
    context.user_data.clear()
    return ConversationHandler.END


async def handle_menu_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    if text == "🛍️ Catálogo":
        await cmd_catalogo(update, context)
    elif text == "📋 Mis pedidos":
        await cmd_mispedidos(update, context)


def client_handlers(app: Application) -> None:
    order_conversation = ConversationHandler(
        entry_points=[
            CommandHandler("pedir", cmd_pedir),
            MessageHandler(filters.Regex("^📦 Hacer pedido$"), cmd_pedir),
        ],
        states={
            SELECT_PRODUCT: [CallbackQueryHandler(handle_product_selection)],
            ENTER_QUANTITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_quantity_input)],
            CONFIRM_ORDER: [CallbackQueryHandler(handle_order_confirmation)],
            ConversationHandler.TIMEOUT: [MessageHandler(filters.ALL, handle_timeout)],
        },
        fallbacks=[CommandHandler("start", cmd_start)],
        conversation_timeout=CONVERSATION_TIMEOUT,
        allow_reentry=True,
    )

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("catalogo", cmd_catalogo))
    app.add_handler(CommandHandler("mispedidos", cmd_mispedidos))
    app.add_handler(order_conversation)
    app.add_handler(
        MessageHandler(
            filters.Regex("^(🛍️ Catálogo|📋 Mis pedidos)$"),
            handle_menu_buttons,
        )
    )
