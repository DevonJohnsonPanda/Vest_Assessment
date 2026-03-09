def test_reconciliation_returns_results(loaded_client):
    resp = loaded_client.get("/reconciliation?date=2025-01-15")
    assert resp.status_code == 200
    body = resp.get_json()
    assert "summary" in body
    assert "discrepancies" in body
    assert "trade_only" in body
    assert "position_only" in body


def test_reconciliation_finds_discrepancies(loaded_client):
    resp = loaded_client.get("/reconciliation?date=2025-01-15")
    body = resp.get_json()
    summary = body["summary"]
    # There should be discrepancies between trades and positions
    assert summary["discrepancies"] > 0


def test_acc001_googl_share_mismatch(loaded_client):
    """ACC001 GOOGL: 200 aggregated trade shares vs 75 position."""
    resp = loaded_client.get("/reconciliation?date=2025-01-15")
    body = resp.get_json()
    googl = [
        d
        for d in body["discrepancies"]
        if d["account_id"] == "ACC001" and d["ticker"] == "GOOGL"
    ]
    assert len(googl) == 1
    assert googl[0]["trade_shares"] == 200.0
    assert googl[0]["position_shares"] == 75.0
    assert googl[0]["share_difference"] == 125.0


def test_position_only_entries(loaded_client):
    """ACC002 TSLA should appear as position-only."""
    resp = loaded_client.get("/reconciliation?date=2025-01-15")
    body = resp.get_json()
    pos_only_keys = {(p["account_id"], p["ticker"]) for p in body["position_only"]}
    # ACC002 TSLA is in positions but not in trades (Format 1 has it under ACC003)
    assert ("ACC002", "TSLA") in pos_only_keys


def test_trade_only_entries(loaded_client):
    """ACC002 GOOGL is in trades but not in positions."""
    resp = loaded_client.get("/reconciliation?date=2025-01-15")
    body = resp.get_json()
    trade_only_keys = {(t["account_id"], t["ticker"]) for t in body["trade_only"]}
    assert ("ACC002", "GOOGL") in trade_only_keys


def test_reconciliation_missing_date(client):
    resp = client.get("/reconciliation")
    assert resp.status_code == 400
