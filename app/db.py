"""Read-only query layer over the SQLite dashboard database.

Revenue figures only count orders with status "Delivered" or "Shipped"
(cancelled/pending orders are excluded from realized revenue, a common
business rule for this kind of report).
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "dashboard.db"

COUNTED_STATUSES = ("Delivered", "Shipped")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_summary(conn: sqlite3.Connection) -> dict:
    placeholders = ",".join("?" * len(COUNTED_STATUSES))
    row = conn.execute(
        f"""
        SELECT
            COALESCE(SUM(oi.quantity * oi.unit_price), 0) AS revenue,
            COALESCE(SUM(oi.quantity), 0) AS units,
            COUNT(DISTINCT o.id) AS orders
        FROM order_items oi
        JOIN orders o ON o.id = oi.order_id
        WHERE o.status IN ({placeholders})
        """,
        COUNTED_STATUSES,
    ).fetchone()

    low_stock = conn.execute(
        "SELECT COUNT(*) AS n FROM products WHERE stock_qty <= reorder_level"
    ).fetchone()["n"]

    revenue = row["revenue"] or 0
    orders = row["orders"] or 0
    return {
        "revenue": round(revenue, 2),
        "units": row["units"] or 0,
        "orders": orders,
        "avg_order_value": round(revenue / orders, 2) if orders else 0.0,
        "low_stock_count": low_stock,
    }


def get_monthly_revenue(conn: sqlite3.Connection) -> list[dict]:
    placeholders = ",".join("?" * len(COUNTED_STATUSES))
    rows = conn.execute(
        f"""
        SELECT strftime('%Y-%m', o.order_date) AS month,
               ROUND(SUM(oi.quantity * oi.unit_price), 2) AS revenue
        FROM order_items oi
        JOIN orders o ON o.id = oi.order_id
        WHERE o.status IN ({placeholders})
        GROUP BY month
        ORDER BY month
        """,
        COUNTED_STATUSES,
    ).fetchall()
    return [dict(r) for r in rows]


def get_top_products(conn: sqlite3.Connection, limit: int = 5) -> list[dict]:
    placeholders = ",".join("?" * len(COUNTED_STATUSES))
    rows = conn.execute(
        f"""
        SELECT p.name AS product,
               ROUND(SUM(oi.quantity * oi.unit_price), 2) AS revenue
        FROM order_items oi
        JOIN orders o ON o.id = oi.order_id
        JOIN products p ON p.id = oi.product_id
        WHERE o.status IN ({placeholders})
        GROUP BY p.name
        ORDER BY revenue DESC
        LIMIT ?
        """,
        (*COUNTED_STATUSES, limit),
    ).fetchall()
    return [dict(r) for r in rows]


def get_orders_by_status(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute(
        """
        SELECT status, COUNT(*) AS n
        FROM orders
        GROUP BY status
        ORDER BY n DESC
        """
    ).fetchall()
    return [dict(r) for r in rows]


def get_stock_alerts(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute(
        """
        SELECT name AS product, category, stock_qty, reorder_level
        FROM products
        WHERE stock_qty <= reorder_level
        ORDER BY (stock_qty * 1.0 / NULLIF(reorder_level, 0)) ASC
        """
    ).fetchall()
    return [dict(r) for r in rows]


def get_revenue_by_region(conn: sqlite3.Connection) -> list[dict]:
    placeholders = ",".join("?" * len(COUNTED_STATUSES))
    rows = conn.execute(
        f"""
        SELECT o.region AS region,
               ROUND(SUM(oi.quantity * oi.unit_price), 2) AS revenue
        FROM order_items oi
        JOIN orders o ON o.id = oi.order_id
        WHERE o.status IN ({placeholders})
        GROUP BY o.region
        ORDER BY revenue DESC
        """,
        COUNTED_STATUSES,
    ).fetchall()
    return [dict(r) for r in rows]
