import io


def test_csv_upload(client):
    data = (
        "TradeDate,AccountID,Ticker,Quantity,Price,TradeType,SettlementDate\n"
        "2025-01-15,ACC001,AAPL,100,185.50,BUY,2025-01-17\n"
    )
    resp = client.post(
        "/ingest",
        data={
            "file": (io.BytesIO(data.encode()), "test.csv"),
        },
    )
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["records_loaded"] == 1
    assert body["errors"] == []


def test_pipe_upload(client):
    data = (
        "REPORT_DATE|ACCOUNT_ID|SECURITY_TICKER|SHARES|MARKET_VALUE|SOURCE_SYSTEM\n"
        "20250115|ACC001|AAPL|100|18550.00|CUSTODIAN_A\n"
    )
    resp = client.post(
        "/ingest",
        data={
            "file": (io.BytesIO(data.encode()), "test.txt"),
        },
    )
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["records_loaded"] == 1


def test_yaml_upload(client):
    data = (
        'report_date: "20250115"\n'
        "positions:\n"
        '  - account_id: "ACC001"\n'
        '    ticker: "AAPL"\n'
        "    shares: 100\n"
        "    market_value: 18550.00\n"
        '    custodian_ref: "REF1"\n'
    )
    resp = client.post(
        "/ingest",
        data={
            "file": (io.BytesIO(data.encode()), "positions.yaml"),
        },
    )
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["records_loaded"] == 1


def test_duplicate_detection(client):
    data = (
        "TradeDate,AccountID,Ticker,Quantity,Price,TradeType,SettlementDate\n"
        "2025-01-15,ACC001,AAPL,100,185.50,BUY,2025-01-17\n"
    )
    client.post("/ingest", data={"file": (io.BytesIO(data.encode()), "dup.csv")})
    resp = client.post("/ingest", data={"file": (io.BytesIO(data.encode()), "dup.csv")})
    body = resp.get_json()
    assert body["duplicates"] == 1
    assert body["records_loaded"] == 0


def test_missing_field_error(client):
    data = (
        "TradeDate,AccountID,Ticker,Quantity,Price,TradeType,SettlementDate\n"
        "2025-01-15,,AAPL,100,185.50,BUY,2025-01-17\n"
    )
    resp = client.post("/ingest", data={"file": (io.BytesIO(data.encode()), "bad.csv")})
    body = resp.get_json()
    assert len(body["errors"]) == 1
    assert body["records_loaded"] == 0


def test_sell_negates_quantity(client):
    from app.database import get_session
    from app.models import Trade

    data = (
        "TradeDate,AccountID,Ticker,Quantity,Price,TradeType,SettlementDate\n"
        "2025-01-15,ACC003,TSLA,150,238.45,SELL,2025-01-17\n"
    )
    client.post("/ingest", data={"file": (io.BytesIO(data.encode()), "sell.csv")})
    session = get_session()
    trade = (
        session.query(Trade).filter_by(ticker="TSLA", source_file="sell.csv").first()
    )
    assert trade.quantity == -150.0
    assert trade.market_value < 0
    session.close()


def test_no_file_returns_400(client):
    resp = client.post("/ingest")
    assert resp.status_code == 400
