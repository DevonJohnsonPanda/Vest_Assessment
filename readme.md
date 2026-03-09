# Portfolio Data Clearinghouse

A Flask-based portfolio data reconciliation system that ingests trade/position data from multiple formats, reconciles discrepancies, and detects compliance violations.

## Setup

```bash
uv sync
uv run flask --app app run
```

## Running Tests

```bash
uv run pytest -v
```

## API Endpoints

### POST /ingest

Upload a trade or position file. Format is auto-detected.

```bash
curl -F "file=@data/trades_format1.csv" http://localhost:5000/ingest
curl -F "file=@data/trades_format2.txt" http://localhost:5000/ingest
curl -F "file=@data/positions.yaml" http://localhost:5000/ingest
```

### GET /positions?account=ACC001&date=2025-01-15

Returns holdings with cost basis and unrealized P&L for an account on a given date.

### GET /compliance/concentration?date=2025-01-15

Returns positions exceeding 20% concentration within their account.

### GET /reconciliation?date=2025-01-15

Compares aggregated trade data against position data, reporting matches, discrepancies, trade-only entries, and position-only entries.

---

## Original Specification

We are building a simplified portfolio data reconciliation system. Our firm receives trade and position data from multiple sources in different formats. We need to ingest this data, reconcile discrepancies, calculate portfolio metrics, and detect compliance violations. A compliance violation for our purposes here occurs when any one equity in an account holds over 20% of the value of that account.

## Key Deliverables

1. Flask application code for endpoints
2. SQLAlchemy models (database schema)
3. Data ingestion logic with quality checks, integrated or separate script
4. Sample test queries or test data showing you validated reconciliation logic
5. Functioning Unit Tests
6. GitHub repository (with access for `autumn-vest` if it needs to be private)
7. README.md

## Requirements

For this exercise, your code should be able to do the following (file examples below):

1. Ingest files of two different formats for daily trades into a single relational database table.
2. Ingest a single format representing our positions from our bank-broker into a second table.
3. Provide several endpoints for the service, via a Python Flask implementation:

| Endpoint | Method | Description |
|---|---|---|
| `/ingest` | POST | Load files, return data quality report (this can also be a script instead) |
| `/positions?account=ACC001&date=2026-01-15` | GET | Positions with cost basis and market value |
| `/compliance/concentration?date=2026-01-15` | GET | Accounts exceeding 20% threshold with breach details |
| `/reconciliation?date=2026-01-15` | GET | Trade vs position file discrepancies on provided day |

The exercise is a vignette of the kind of work you would be engaged in at Vest. We don't expect you to have specific knowledge of the markets, so please don't hesitate to reach out if you have any questions as you work through this exercise: apatterson@vestfin.com

---

## Appendix A - Data Examples

### Trade File Format 1

CSV format with comma delimiter:

```csv
TradeDate,AccountID,Ticker,Quantity,Price,TradeType,SettlementDate
2025-01-15,ACC001,AAPL,100,185.50,BUY,2025-01-17
2025-01-15,ACC001,MSFT,50,420.25,BUY,2025-01-17
2025-01-15,ACC002,GOOGL,75,142.80,BUY,2025-01-17
2025-01-15,ACC002,AAPL,200,185.50,BUY,2025-01-17
2025-01-15,ACC003,TSLA,150,238.45,SELL,2025-01-17
2025-01-15,ACC003,NVDA,80,505.30,BUY,2025-01-17
2025-01-15,ACC001,GOOGL,100,142.80,BUY,2025-01-17
2025-01-15,ACC004,AAPL,500,185.50,BUY,2025-01-17
2025-01-15,ACC004,MSFT,300,420.25,BUY,2025-01-17
2025-01-15,ACC002,NVDA,120,505.30,BUY,2025-01-17
```

### Trade File Format 2

Pipe-delimited format:

```
REPORT_DATE|ACCOUNT_ID|SECURITY_TICKER|SHARES|MARKET_VALUE|SOURCE_SYSTEM
20250115|ACC001|AAPL|100|18550.00|CUSTODIAN_A
20250115|ACC001|MSFT|50|21012.50|CUSTODIAN_A
20250115|ACC001|GOOGL|100|14280.00|CUSTODIAN_A
20250115|ACC002|GOOGL|75|10710.00|CUSTODIAN_B
20250115|ACC002|AAPL|200|37100.00|CUSTODIAN_B
20250115|ACC002|NVDA|120|60636.00|CUSTODIAN_B
20250115|ACC003|TSLA|-150|-35767.50|CUSTODIAN_A
20250115|ACC003|NVDA|80|40424.00|CUSTODIAN_A
20250115|ACC004|AAPL|500|92750.00|CUSTODIAN_C
20250115|ACC004|MSFT|300|126075.00|CUSTODIAN_C
```

### Bank Position Format

YAML format:

```yaml
report_date: "20250115"
positions:
  - account_id: "ACC001"
    ticker: "AAPL"
    shares: 100
    market_value: 18550.00
    custodian_ref: "CUST_A_12345"
  - account_id: "ACC001"
    ticker: "MSFT"
    shares: 50
    market_value: 21012.50
    custodian_ref: "CUST_A_12346"
  - account_id: "ACC001"
    ticker: "GOOGL"
    shares: 75
    market_value: 10710.00
    custodian_ref: "CUST_A_12347"
  - account_id: "ACC002"
    ticker: "AAPL"
    shares: 200
    market_value: 37100.00
    custodian_ref: "CUST_B_22345"
  - account_id: "ACC002"
    ticker: "NVDA"
    shares: 120
    market_value: 60636.00
    custodian_ref: "CUST_B_22346"
  - account_id: "ACC002"
    ticker: "TSLA"
    shares: 80
    market_value: 19076.00
    custodian_ref: "CUST_B_22347"
  - account_id: "ACC003"
    ticker: "MSFT"
    shares: 150
    market_value: 63037.50
    custodian_ref: "CUST_A_32345"
  - account_id: "ACC003"
    ticker: "GOOGL"
    shares: 100
    market_value: 14280.00
    custodian_ref: "CUST_A_32346"
  - account_id: "ACC003"
    ticker: "AAPL"
    shares: 50
    market_value: 9275.00
    custodian_ref: "CUST_A_32347"
```
