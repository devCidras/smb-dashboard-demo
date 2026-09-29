"""FastAPI app serving the SMB dashboard: sales, stock and orders KPIs
backed by SQLite. Run with:

    uvicorn app.main:app --reload
"""

import json
import sys
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from . import db

BASE_DIR = Path(__file__).parent

app = FastAPI(title="SMB Dashboard")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.on_event("startup")
def _ensure_seeded() -> None:
    # Hosting platforms with an ephemeral disk (e.g. Render's free tier)
    # can wipe data/ between deploys, so (re)seed automatically if the
    # database is missing instead of requiring a manual step.
    if not db.DB_PATH.exists():
        sys.path.insert(0, str(BASE_DIR.parent))
        import seed_data

        seed_data.main()


def _dashboard_data() -> dict:
    conn = db.get_connection()
    try:
        return {
            "summary": db.get_summary(conn),
            "monthly_revenue": db.get_monthly_revenue(conn),
            "top_products": db.get_top_products(conn),
            "orders_by_status": db.get_orders_by_status(conn),
            "stock_alerts": db.get_stock_alerts(conn),
            "revenue_by_region": db.get_revenue_by_region(conn),
        }
    finally:
        conn.close()


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    data = _dashboard_data()
    # Escape "</" so a value containing e.g. "</script>" can't break out of
    # the inline <script type="application/json"> block (JSON.parse still
    # sees a valid document: "<\/" is a standard JSON-escaped "/").
    safe_json = json.dumps(data).replace("</", "<\\/")
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={"data": data, "data_json": safe_json},
    )


@app.get("/api/summary")
def api_summary():
    conn = db.get_connection()
    try:
        return db.get_summary(conn)
    finally:
        conn.close()


@app.get("/api/monthly-revenue")
def api_monthly_revenue():
    conn = db.get_connection()
    try:
        return db.get_monthly_revenue(conn)
    finally:
        conn.close()


@app.get("/api/top-products")
def api_top_products():
    conn = db.get_connection()
    try:
        return db.get_top_products(conn)
    finally:
        conn.close()


@app.get("/api/stock-alerts")
def api_stock_alerts():
    conn = db.get_connection()
    try:
        return db.get_stock_alerts(conn)
    finally:
        conn.close()
