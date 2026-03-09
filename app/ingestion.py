import csv
import io
from datetime import datetime

import yaml
from sqlalchemy.exc import IntegrityError

from app.database import get_session
from app.models import Position, Trade


def parse_trade_csv(file_content: str, filename: str = "trades_format1.csv") -> dict:
    """Parse Format 1 CSV trades. Returns quality report."""
    reader = csv.DictReader(io.StringIO(file_content))
    records = []
    errors = []
    row_num = 1

    for row in reader:
        row_num += 1
        try:
            required = (
                "TradeDate",
                "AccountID",
                "Ticker",
                "Quantity",
                "Price",
                "TradeType",
            )
            for field in required:
                if not row.get(field, "").strip():
                    raise ValueError(f"Missing required field: {field}")

            trade_date = datetime.strptime(row["TradeDate"], "%Y-%m-%d").date()
            quantity = float(row["Quantity"])
            price = float(row["Price"])
            trade_type = row["TradeType"].upper()

            if trade_type not in ("BUY", "SELL"):
                raise ValueError(f"Invalid trade type: {trade_type}")
            if trade_type == "BUY" and quantity < 0:
                raise ValueError("Negative quantity on BUY trade")

            signed_qty = -abs(quantity) if trade_type == "SELL" else abs(quantity)
            market_value = signed_qty * price

            settlement_date = None
            if row.get("SettlementDate", "").strip():
                settlement_date = datetime.strptime(
                    row["SettlementDate"], "%Y-%m-%d"
                ).date()

            records.append(
                Trade(
                    trade_date=trade_date,
                    account_id=row["AccountID"].strip(),
                    ticker=row["Ticker"].strip(),
                    quantity=signed_qty,
                    price=price,
                    market_value=market_value,
                    trade_type=trade_type,
                    settlement_date=settlement_date,
                    source_file=filename,
                )
            )
        except (ValueError, KeyError) as e:
            errors.append({"row": row_num, "error": str(e)})

    return _save_trades(records, errors, filename)


def parse_trade_pipe(file_content: str, filename: str = "trades_format2.txt") -> dict:
    """Parse Format 2 pipe-delimited trades. Returns quality report."""
    lines = file_content.strip().splitlines()
    if not lines:
        return _empty_report(filename)

    records = []
    errors = []

    for i, line in enumerate(lines[1:], start=2):
        try:
            parts = line.split("|")
            if len(parts) < 6:
                raise ValueError("Insufficient fields")

            report_date = datetime.strptime(parts[0], "%Y%m%d").date()
            shares = float(parts[3])
            market_value = float(parts[4])
            trade_type = "SELL" if shares < 0 else "BUY"

            records.append(
                Trade(
                    trade_date=report_date,
                    account_id=parts[1].strip(),
                    ticker=parts[2].strip(),
                    quantity=shares,
                    price=None,
                    market_value=market_value,
                    trade_type=trade_type,
                    source_system=parts[5].strip(),
                    source_file=filename,
                )
            )
        except (ValueError, IndexError) as e:
            errors.append({"row": i, "error": str(e)})

    return _save_trades(records, errors, filename)


def parse_positions_yaml(file_content: str, filename: str = "positions.yaml") -> dict:
    """Parse YAML positions file. Returns quality report."""
    data = yaml.safe_load(file_content)
    if not data or "positions" not in data:
        report = _empty_report(filename)
        report["errors"] = ["No positions found"]
        return report

    report_date = datetime.strptime(str(data["report_date"]), "%Y%m%d").date()
    records = []
    errors = []

    for i, pos in enumerate(data["positions"], start=1):
        try:
            required = (
                "account_id",
                "ticker",
                "shares",
                "market_value",
                "custodian_ref",
            )
            for field in required:
                if field not in pos:
                    raise ValueError(f"Missing required field: {field}")

            records.append(
                Position(
                    report_date=report_date,
                    account_id=str(pos["account_id"]).strip(),
                    ticker=str(pos["ticker"]).strip(),
                    shares=float(pos["shares"]),
                    market_value=float(pos["market_value"]),
                    custodian_ref=str(pos["custodian_ref"]).strip(),
                )
            )
        except (ValueError, KeyError) as e:
            errors.append({"position": i, "error": str(e)})

    duplicates = 0
    loaded = 0
    session = get_session()
    try:
        for record in records:
            try:
                session.add(record)
                session.flush()
                loaded += 1
            except IntegrityError:
                session.rollback()
                duplicates += 1
        session.commit()
    finally:
        session.close()

    return {
        "file": filename,
        "records_processed": len(records),
        "records_loaded": loaded,
        "errors": errors,
        "duplicates": duplicates,
    }


def _empty_report(filename: str) -> dict:
    return {
        "file": filename,
        "records_processed": 0,
        "records_loaded": 0,
        "errors": [],
        "duplicates": 0,
    }


def _save_trades(records: list, errors: list, filename: str) -> dict:
    duplicates = 0
    loaded = 0
    session = get_session()
    try:
        for record in records:
            try:
                session.add(record)
                session.flush()
                loaded += 1
            except IntegrityError:
                session.rollback()
                duplicates += 1
        session.commit()
    finally:
        session.close()

    return {
        "file": filename,
        "records_processed": len(records),
        "records_loaded": loaded,
        "errors": errors,
        "duplicates": duplicates,
    }


def detect_and_parse(file_content: str, filename: str) -> dict:
    """Auto-detect file format and parse accordingly."""
    if filename.endswith((".yaml", ".yml")):
        return parse_positions_yaml(file_content, filename)

    first_line = file_content.strip().splitlines()[0] if file_content.strip() else ""
    if "|" in first_line:
        return parse_trade_pipe(file_content, filename)

    return parse_trade_csv(file_content, filename)
