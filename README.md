# 🤖 OrderBot — Telegram Order Management Bot

> **Demo project** built to showcase production-ready Python bot development skills.  
> **Proyecto demo** para demostrar capacidades en desarrollo de bots con Python.

---

## 🇲🇽 Español

### Descripción

**OrderBot** es un bot de Telegram completo para gestión de pedidos en tiempo real. Permite a clientes explorar un catálogo, realizar pedidos mediante un flujo conversacional guiado y consultar su historial. Los administradores pueden gestionar todos los pedidos, actualizar estados y recibir notificaciones automáticas, todo desde Telegram.

> 💡 *Este proyecto fue desarrollado como demo de capacidades en desarrollo de bots con Python para portafolio profesional.*

### ✨ Features principales

- 🛒 **Flujo de pedido conversacional** — selección de producto, cantidad y confirmación paso a paso
- 📦 **Catálogo dinámico** — productos con precio consultados desde la base de datos
- 📋 **Historial de pedidos** — el cliente ve todos sus pedidos y su estado actual
- 🔔 **Notificaciones en tiempo real** — el admin recibe cada nuevo pedido; el cliente recibe cada cambio de estado
- 🔧 **Panel de administración** — gestión de pedidos activos con botones inline
- 📊 **Estadísticas** — totales diarios/semanales, desglose por estado, producto más vendido
- ⏰ **Timeout automático** — los flujos de conversación expiran tras 5 minutos de inactividad
- 📝 **Logs rotativos** — archivo `orderbot.log` con rotación automática

### 🛠️ Stack tecnológico

| Capa | Tecnología |
|------|-----------|
| Lenguaje | Python 3.11+ |
| Bot framework | python-telegram-bot ≥ 20.0 (async) |
| Base de datos | SQLite + aiosqlite |
| Config | python-dotenv |

### 📁 Estructura del proyecto

```
orderbot/
├── .env.example          # Variables de entorno requeridas
├── main.py               # Punto de entrada, logging y arranque
├── config.py             # Constantes y variables de entorno
├── database.py           # Capa de acceso a datos (async)
├── handlers/
│   ├── client.py         # Comandos y ConversationHandler del cliente
│   └── admin.py          # Panel de administración y callbacks
├── models/
│   └── order.py          # Dataclasses Order y Product
└── utils/
    └── keyboards.py      # Teclados inline y reply
```

### ⚙️ Instalación paso a paso

**1. Clona el repositorio**
```bash
git clone https://github.com/tu-usuario/orderbot.git
cd orderbot
```

**2. Crea un entorno virtual**
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

**3. Instala las dependencias**
```bash
pip install python-telegram-bot[job-queue]>=20.0 aiosqlite python-dotenv
```

**4. Configura las variables de entorno**
```bash
cp .env.example .env
# Edita .env con tus credenciales
```

**5. Ejecuta el bot**
```bash
python main.py
```

### 🔑 Configuración del .env

```env
TELEGRAM_TOKEN=123456789:ABCDefgh...   # Token de @BotFather
ADMIN_ID=987654321                      # Tu Telegram user ID (usa @userinfobot)
```

### 💬 Comandos disponibles

**Clientes**
| Comando | Descripción |
|---------|-------------|
| `/start` | Bienvenida y menú principal |
| `/catalogo` | Ver productos disponibles |
| `/pedir` | Iniciar un nuevo pedido |
| `/mispedidos` | Ver historial de pedidos |

**Administrador**
| Comando | Descripción |
|---------|-------------|
| `/admin` | Panel de administración |
| `/pedidos` | Ver pedidos activos |
| `/estadisticas` | Ver estadísticas del negocio |

### 📸 Capturas de pantalla

| Menú principal | Catálogo | Flujo de pedido |
|:-:|:-:|:-:|
| `[screenshot_menu.png]` | `[screenshot_catalog.png]` | `[screenshot_order.png]` |

| Panel admin | Estadísticas |
|:-:|:-:|
| `[screenshot_admin.png]` | `[screenshot_stats.png]` |

### 🔄 Ciclo de vida de un pedido

```
pendiente → confirmado → en preparación → enviado → entregado
```

Cada transición notifica automáticamente al cliente por Telegram.

---

## 🇺🇸 English

### Description

**OrderBot** is a full-featured Telegram bot for real-time order management. Customers can browse a product catalog, place orders through a guided conversational flow, and check their order history. Admins can manage all orders, update statuses, and receive instant notifications — all within Telegram.

> 💡 *This project was built as a demo of Python bot development capabilities for a professional portfolio.*

### ✨ Key Features

- 🛒 **Conversational order flow** — step-by-step product selection, quantity input, and confirmation
- 📦 **Dynamic catalog** — products and prices fetched from SQLite database
- 📋 **Order history** — customers view all their orders and current statuses
- 🔔 **Real-time notifications** — admin is notified on every new order; customers on every status change
- 🔧 **Admin panel** — manage active orders with inline buttons directly in Telegram
- 📊 **Statistics** — daily/weekly totals, breakdown by status, top-selling product
- ⏰ **Auto-timeout** — conversation flows expire after 5 minutes of inactivity
- 📝 **Rotating logs** — `orderbot.log` with automatic file rotation

### 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.11+ |
| Bot framework | python-telegram-bot ≥ 20.0 (async) |
| Database | SQLite + aiosqlite |
| Config | python-dotenv |

### ⚙️ Installation

**1. Clone the repository**
```bash
git clone https://github.com/your-username/orderbot.git
cd orderbot
```

**2. Create a virtual environment**
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

**3. Install dependencies**
```bash
pip install python-telegram-bot[job-queue]>=20.0 aiosqlite python-dotenv
```

**4. Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your credentials
```

**5. Run the bot**
```bash
python main.py
```

### 🔑 Environment Variables

```env
TELEGRAM_TOKEN=123456789:ABCDefgh...   # Token from @BotFather
ADMIN_ID=987654321                      # Your Telegram user ID (use @userinfobot)
```

### 🔄 Order Lifecycle

```
pending → confirmed → preparing → shipped → delivered
```

Every transition automatically notifies the customer via Telegram.

---

## 📄 License

MIT License — feel free to use this project as a base for your own bots.

---

<div align="center">
  <sub>Built with ❤️ using Python & python-telegram-bot</sub>
</div>
