def test_positions_requires_params(client):
    resp = client.get("/positions")
    assert resp.status_code == 400


def test_positions_missing_account(client):
    resp = client.get("/positions?date=2025-01-15")
    assert resp.status_code == 400


def test_positions_returns_holdings(loaded_client):
    resp = loaded_client.get("/positions?account=ACC001&date=2025-01-15")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["account"] == "ACC001"
    assert len(body["holdings"]) == 3

    tickers = {h["ticker"] for h in body["holdings"]}
    assert tickers == {"AAPL", "MSFT", "GOOGL"}


def test_positions_cost_basis(loaded_client):
    resp = loaded_client.get("/positions?account=ACC001&date=2025-01-15")
    body = resp.get_json()
    aapl = next(h for h in body["holdings"] if h["ticker"] == "AAPL")
    # BUY 100@185.50 from F1 + 100 shares from F2 (mv=18550)
    assert aapl["cost_basis"] == 37100.0
    # Position market_value is 18550, cost_basis is 37100
    assert aapl["unrealized_pnl"] == 18550.0 - 37100.0


def test_positions_empty_account(loaded_client):
    resp = loaded_client.get("/positions?account=NONEXIST&date=2025-01-15")
    assert resp.status_code == 200
    assert resp.get_json()["holdings"] == []
