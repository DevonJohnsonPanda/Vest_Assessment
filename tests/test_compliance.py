def test_concentration_violations(loaded_client):
    resp = loaded_client.get("/compliance/concentration?date=2025-01-15")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["violations_count"] > 0

    # Check that violations have required fields
    for v in body["violations"]:
        assert "account_id" in v
        assert "ticker" in v
        assert "concentration_pct" in v
        assert v["concentration_pct"] > 20.0


def test_concentration_no_data(loaded_client):
    resp = loaded_client.get("/compliance/concentration?date=2024-01-01")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["violations_count"] == 0


def test_concentration_missing_date(client):
    resp = client.get("/compliance/concentration")
    assert resp.status_code == 400


def test_acc002_nvda_is_violation(loaded_client):
    """ACC002 has NVDA at 60636 which is >20% of account total."""
    resp = loaded_client.get("/compliance/concentration?date=2025-01-15")
    body = resp.get_json()
    nvda_violations = [
        v
        for v in body["violations"]
        if v["account_id"] == "ACC002" and v["ticker"] == "NVDA"
    ]
    assert len(nvda_violations) == 1
    assert nvda_violations[0]["concentration_pct"] > 20.0
