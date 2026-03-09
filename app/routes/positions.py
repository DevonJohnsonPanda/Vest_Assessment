from datetime import datetime

from flask import Blueprint, Response, jsonify, request
from sqlalchemy import select

from app.database import get_session
from app.models import Position, Trade

bp = Blueprint("positions", __name__)


@bp.route("/positions", methods=["GET"])
def get_positions() -> tuple[Response, int]:
    account = request.args.get("account")
    date_str = request.args.get("date")

    if not account or not date_str:
        msg = "Both 'account' and 'date' parameters are required"
        return jsonify({"error": msg}), 400

    try:
        report_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Invalid date format, use YYYY-MM-DD"}), 400

    session = get_session()
    try:
        positions = (
            session.execute(
                select(Position).where(
                    Position.account_id == account,
                    Position.report_date == report_date,
                )
            )
            .scalars()
            .all()
        )

        if not positions:
            return jsonify({"account": account, "date": date_str, "holdings": []}), 200

        # Compute cost basis from BUY trades up to this date
        buy_trades = (
            session.execute(
                select(Trade).where(
                    Trade.account_id == account,
                    Trade.trade_date <= report_date,
                    Trade.trade_type == "BUY",
                )
            )
            .scalars()
            .all()
        )

        cost_basis_map: dict[str, float] = {}
        for t in buy_trades:
            prev = cost_basis_map.get(t.ticker, 0.0)
            if t.price is not None:
                cost_basis_map[t.ticker] = prev + t.quantity * t.price
            elif t.market_value is not None:
                cost_basis_map[t.ticker] = prev + t.market_value

        holdings = []
        for pos in positions:
            cost_basis = round(cost_basis_map.get(pos.ticker, 0.0), 2)
            holdings.append(
                {
                    "ticker": pos.ticker,
                    "shares": pos.shares,
                    "market_value": pos.market_value,
                    "cost_basis": cost_basis,
                    "unrealized_pnl": round(pos.market_value - cost_basis, 2),
                    "custodian_ref": pos.custodian_ref,
                }
            )

        return jsonify(
            {
                "account": account,
                "date": date_str,
                "holdings": holdings,
            }
        ), 200
    finally:
        session.close()
