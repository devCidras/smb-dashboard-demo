from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_dashboard_page_renders(seeded_db_path):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "SMB Dashboard" in resp.text


def test_dashboard_escapes_script_closing_tag(seeded_db_path, monkeypatch):
    from app import main as main_module

    def fake_dashboard_data():
        return {
            "summary": {"revenue": 0, "units": 0, "orders": 0, "avg_order_value": 0, "low_stock_count": 0},
            "monthly_revenue": [],
            "top_products": [],
            "orders_by_status": [],
            "stock_alerts": [],
            "revenue_by_region": [],
            "malicious": "</script><script>alert(1)</script>",
        }

    monkeypatch.setattr(main_module, "_dashboard_data", fake_dashboard_data)
    resp = client.get("/")
    assert resp.status_code == 200
    assert "<script>alert(1)</script>" not in resp.text
    assert "<\\/script><script>alert(1)<\\/script>" in resp.text


def test_api_summary_endpoint(seeded_db_path):
    resp = client.get("/api/summary")
    assert resp.status_code == 200
    body = resp.json()
    assert body["revenue"] == 40.0
    assert body["orders"] == 1


def test_api_stock_alerts_endpoint(seeded_db_path):
    resp = client.get("/api/stock-alerts")
    assert resp.status_code == 200
    assert [p["product"] for p in resp.json()] == ["Widget"]
