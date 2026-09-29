import sqlite3

import pytest

SCHEMA = """
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    unit_price REAL NOT NULL,
    stock_qty INTEGER NOT NULL,
    reorder_level INTEGER NOT NULL
);

CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    order_date TEXT NOT NULL,
    customer TEXT NOT NULL,
    region TEXT NOT NULL,
    status TEXT NOT NULL
);

CREATE TABLE order_items (
    id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL
);
"""

PRODUCTS = [
    (1, "Widget", "Tools", 10.0, 2, 5),  # below reorder level -> stock alert
    (2, "Gadget", "Tools", 20.0, 50, 5),  # healthy stock
]

ORDERS = [
    (1, "2026-01-15", "Alice", "North", "Delivered"),
    (2, "2026-01-20", "Bob", "South", "Pending"),
    (3, "2026-02-01", "Carol", "North", "Cancelled"),
]

ORDER_ITEMS = [
    (1, 1, 2, 10.0),  # order 1 (Delivered): 20
    (1, 2, 1, 20.0),  # order 1 (Delivered): 20
    (2, 2, 1, 20.0),  # order 2 (Pending): excluded from revenue
    (3, 1, 5, 10.0),  # order 3 (Cancelled): excluded from revenue
]


def build_seeded_db(path) -> None:
    connection = sqlite3.connect(path)
    connection.executescript(SCHEMA)
    connection.executemany(
        "INSERT INTO products (id, name, category, unit_price, stock_qty, reorder_level) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        PRODUCTS,
    )
    connection.executemany(
        "INSERT INTO orders (id, order_date, customer, region, status) VALUES (?, ?, ?, ?, ?)",
        ORDERS,
    )
    connection.executemany(
        "INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?)",
        ORDER_ITEMS,
    )
    connection.commit()
    connection.close()


@pytest.fixture()
def seeded_connection(tmp_path):
    db_path = tmp_path / "test.db"
    build_seeded_db(db_path)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    yield connection
    connection.close()


@pytest.fixture()
def seeded_db_path(tmp_path, monkeypatch):
    from app import db

    db_path = tmp_path / "test.db"
    build_seeded_db(db_path)
    monkeypatch.setattr(db, "DB_PATH", db_path)
    return db_path
