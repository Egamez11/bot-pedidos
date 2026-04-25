from dataclasses import dataclass
from datetime import datetime


@dataclass
class Product:
    id: int
    name: str
    price: float
    description: str
    available: bool

    def format_price(self) -> str:
        return f"${self.price:.0f} MXN"

    def to_catalog_line(self) -> str:
        return f"• *{self.name}* — {self.format_price()}\n  _{self.description}_"


@dataclass
class Order:
    id: int
    client_id: int
    client_name: str
    product: str
    quantity: int
    status: str
    created_at: datetime
    updated_at: datetime

    @property
    def summary(self) -> str:
        lines = [
            f"📦 *Pedido #{self.id}*",
            f"👤 Cliente: {self.client_name}",
            f"🍔 Producto: {self.product}",
            f"🔢 Cantidad: {self.quantity}",
            f"📊 Status: {self.status}",
            f"🕐 Creado: {self.created_at.strftime('%d/%m/%Y %H:%M')}",
        ]
        return "\n".join(lines)
