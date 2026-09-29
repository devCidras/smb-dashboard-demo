"""Seeds a SQLite database with realistic sales/stock/orders data for the
dashboard demo: a small business selling office furniture and electronics,
with ~6 months of orders and a product catalog where a few items are
intentionally below their reorder level (to populate the stock-alert panel).
"""

import random
import sqlite3
from datetime import date, timedelta
from pathlib import Path

random.seed(7)

DB_PATH = Path(__file__).parent / "data" / "dashboard.db"

PRODUCTS = [
    # name, category, unit_price, stock_qty, reorder_level
    ("Office Chair", "Furniture", 89.90, 42, 15),
    ("Adjustable Desk", "Furniture", 249.00, 8, 10),
    ("24in Monitor", "Electronics", 139.50, 27, 12),
    ("Mechanical Keyboard", "Electronics", 59.90, 4, 15),
    ("Wireless Mouse", "Electronics", 24.90, 55, 20),
    ("LED Desk Lamp", "Lighting", 34.50, 33, 10),
    ("Modular Shelving Unit", "Furniture", 119.00, 6, 8),
    ("Bluetooth Headphones", "Electronics", 79.00, 18, 12),
    ("XL Mouse Pad", "Accessories", 14.90, 61, 20),
    ("HD Webcam", "Electronics", 44.90, 9, 10),
]

REGIONS = ["North", "South", "East", "West", "Central"]
CUSTOMERS = [f"Customer {i:03d}" for i in range(1, 41)]
STATUSES = ["Delivered", "Shipped", "Pending", "Cancelled"]
STATUS_WEIGHTS = [0.62, 0.18, 0.12, 0.08]

SCHEMA = """
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    unit_price REAL NOT NULL,
    stock_qty INTEGER NOT NULL,
    reorder_level INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY,
    order_date TEXT NOT NULL,
    customer TEXT NOT NULL,
    region TEXT NOT NULL,
    status TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id),
    product_id INTEGER NOT NULL REFERENCES products(id),
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL
);
"""


def build_orders(conn: sqlite3.Connection, num_orders: int = 260) -> None:
    cur = conn.cursor()
    start = date(2026, 3, 1)
    for _ in range(num_orders):
        order_date = start + timedelta(days=random.randint(0, 209))  # ~7 months
        status = random.choices(STATUSES, weights=STATUS_WEIGHTS, k=1)[0]
        cur.execute(
            "INSERT INTO orders (order_date, customer, region, status) VALUES (?, ?, ?, ?)",
            (order_date.isoformat(), random.choice(CUSTOMERS), random.choice(REGIONS), status),
        )
        order_id = cur.lastrowid

        for _ in range(random.randint(1, 4)):
            product_id = random.randint(1, len(PRODUCTS))
            _, _, unit_price, _, _ = PRODUCTS[product_id - 1]
            qty = random.randint(1, 5)
            cur.execute(
                "INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?)",
                (order_id, product_id, qty, unit_price),
            )
    conn.commit()


def main() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)

    conn.executemany(
        "INSERT INTO products (name, category, unit_price, stock_qty, reorder_level) VALUES (?, ?, ?, ?, ?)",
        PRODUCTS,
    )
    conn.commit()

    build_orders(conn)
    conn.close()

    print(f"Database created: {DB_PATH}")


if __name__ == "__main__":
    main()
