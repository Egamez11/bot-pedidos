import logging
from datetime import datetime, timedelta

import aiosqlite

from config import DATABASE_URL
from models import Order, Product

logger = logging.getLogger(__name__)

DEMO_PRODUCTS = [
    ("Burger Clásica", 85.0, "Carne 200g, lechuga, tomate, queso", True),
    ("Burger BBQ", 95.0, "Carne 200g, cheddar, tocino, salsa BBQ", True),
    ("Papas Fritas", 45.0, "Porción mediana con aderezo", True),
    ("Refresco", 30.0, "355ml, sabor a elegir", True),
    ("Combo Burger + Papas + Refresco", 145.0, "Burger clásica + papas + refresco", True),
]


async def init_db() -> None:
    async with aiosqlite.connect(DATABASE_URL) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT    NOT NULL UNIQUE,
                price       REAL    NOT NULL,
                description TEXT    NOT NULL DEFAULT '',
                available   INTEGER NOT NULL DEFAULT 1
            )
            """
        )
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS orders (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id   INTEGER NOT NULL,
                client_name TEXT    NOT NULL,
                product     TEXT    NOT NULL,
                quantity    INTEGER NOT NULL,
                status      TEXT    NOT NULL DEFAULT 'pendiente',
                created_at  TEXT    NOT NULL,
                updated_at  TEXT    NOT NULL
            )
            """
        )
        await _seed_products(db)
        await db.commit()
    logger.info("Base de datos inicializada correctamente.")


async def _seed_products(db: aiosqlite.Connection) -> None:
    for name, price, description, available in DEMO_PRODUCTS:
        await db.execute(
            """
            INSERT OR IGNORE INTO products (name, price, description, available)
            VALUES (?, ?, ?, ?)
            """,
            (name, price, description, int(available)),
        )


async def get_available_products() -> list[Product]:
    async with aiosqlite.connect(DATABASE_URL) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM products WHERE available = 1 ORDER BY id"
        ) as cursor:
            rows = await cursor.fetchall()
    return [_row_to_product(r) for r in rows]


async def get_product_by_id(product_id: int) -> Product | None:
    async with aiosqlite.connect(DATABASE_URL) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM products WHERE id = ?", (product_id,)
        ) as cursor:
            row = await cursor.fetchone()
    return _row_to_product(row) if row else None


async def create_order(
    client_id: int,
    client_name: str,
    product: str,
    quantity: int,
) -> int:
    now = datetime.now().isoformat()
    async with aiosqlite.connect(DATABASE_URL) as db:
        cursor = await db.execute(
            """
            INSERT INTO orders (client_id, client_name, product, quantity, status,
                                created_at, updated_at)
            VALUES (?, ?, ?, ?, 'pendiente', ?, ?)
            """,
            (client_id, client_name, product, quantity, now, now),
        )
        order_id = cursor.lastrowid
        await db.commit()
    logger.info("Pedido #%d creado para cliente %d.", order_id, client_id)
    return order_id


async def get_orders_by_client(client_id: int) -> list[Order]:
    async with aiosqlite.connect(DATABASE_URL) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM orders WHERE client_id = ? ORDER BY created_at DESC",
            (client_id,),
        ) as cursor:
            rows = await cursor.fetchall()
    return [_row_to_order(r) for r in rows]


async def get_active_orders() -> list[Order]:
    async with aiosqlite.connect(DATABASE_URL) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """
            SELECT * FROM orders
            WHERE status != 'entregado'
            ORDER BY created_at ASC
            """
        ) as cursor:
            rows = await cursor.fetchall()
    return [_row_to_order(r) for r in rows]


async def get_order_by_id(order_id: int) -> Order | None:
    async with aiosqlite.connect(DATABASE_URL) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM orders WHERE id = ?", (order_id,)
        ) as cursor:
            row = await cursor.fetchone()
    return _row_to_order(row) if row else None


async def update_order_status(order_id: int, new_status: str) -> None:
    now = datetime.now().isoformat()
    async with aiosqlite.connect(DATABASE_URL) as db:
        await db.execute(
            "UPDATE orders SET status = ?, updated_at = ? WHERE id = ?",
            (new_status, now, order_id),
        )
        await db.commit()
    logger.info("Pedido #%d actualizado a '%s'.", order_id, new_status)


async def get_statistics() -> dict:
    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    week_start = (now - timedelta(days=now.weekday())).replace(
        hour=0, minute=0, second=0, microsecond=0
    ).isoformat()

    async with aiosqlite.connect(DATABASE_URL) as db:
        db.row_factory = aiosqlite.Row

        async with db.execute(
            "SELECT COUNT(*) AS total FROM orders WHERE created_at >= ?", (today_start,)
        ) as cur:
            today_total = (await cur.fetchone())["total"]

        async with db.execute(
            "SELECT COUNT(*) AS total FROM orders WHERE created_at >= ?", (week_start,)
        ) as cur:
            week_total = (await cur.fetchone())["total"]

        async with db.execute(
            "SELECT status, COUNT(*) AS qty FROM orders GROUP BY status"
        ) as cur:
            by_status = {row["status"]: row["qty"] for row in await cur.fetchall()}

        async with db.execute(
            """
            SELECT product, COUNT(*) AS qty
            FROM orders
            GROUP BY product
            ORDER BY qty DESC
            LIMIT 1
            """
        ) as cur:
            top_row = await cur.fetchone()
            top_product = (top_row["product"], top_row["qty"]) if top_row else ("—", 0)

    return {
        "today": today_total,
        "week": week_total,
        "by_status": by_status,
        "top_product": top_product,
    }


def _row_to_product(row: aiosqlite.Row) -> Product:
    return Product(
        id=row["id"],
        name=row["name"],
        price=row["price"],
        description=row["description"],
        available=bool(row["available"]),
    )


def _row_to_order(row: aiosqlite.Row) -> Order:
    return Order(
        id=row["id"],
        client_id=row["client_id"],
        client_name=row["client_name"],
        product=row["product"],
        quantity=row["quantity"],
        status=row["status"],
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )
