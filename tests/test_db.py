from app import db


def test_get_summary_counts_only_delivered_and_shipped(seeded_connection):
    summary = db.get_summary(seeded_connection)
    assert summary["revenue"] == 40.0
    assert summary["units"] == 3
    assert summary["orders"] == 1
    assert summary["low_stock_count"] == 1


def test_get_stock_alerts_flags_low_stock_only(seeded_connection):
    alerts = db.get_stock_alerts(seeded_connection)
    assert [a["product"] for a in alerts] == ["Widget"]


def test_get_orders_by_status_counts_all_statuses(seeded_connection):
    rows = {r["status"]: r["n"] for r in db.get_orders_by_status(seeded_connection)}
    assert rows == {"Delivered": 1, "Pending": 1, "Cancelled": 1}


def test_get_revenue_by_region_excludes_non_counted_statuses(seeded_connection):
    rows = {r["region"]: r["revenue"] for r in db.get_revenue_by_region(seeded_connection)}
    assert rows == {"North": 40.0}


def test_get_monthly_revenue_groups_by_month(seeded_connection):
    rows = {r["month"]: r["revenue"] for r in db.get_monthly_revenue(seeded_connection)}
    assert rows == {"2026-01": 40.0}
