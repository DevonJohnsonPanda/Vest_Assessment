from datetime import date

from sqlalchemy import select

from app.database import get_session
from app.models import Position, Trade


def reconcile(report_date: date) -> dict:
    """Compare aggregated trades against positions for a given date."""
    session = get_session()
    try:
        trades = (
            session.execute(select(Trade).where(Trade.trade_date <= report_date))
            .scalars()
            .all()
        )

        positions = (
            session.execute(select(Position).where(Position.report_date == report_date))
            .scalars()
            .all()
        )

        # Aggregate trade shares by (account_id, ticker)
        trade_agg: dict[tuple[str, str], float] = {}
        for t in trades:
            key = (t.account_id, t.ticker)
            if key not in trade_agg:
                trade_agg[key] = 0.0
            trade_agg[key] += t.quantity

        # Index positions
        pos_map: dict[tuple[str, str], Position] = {}
        for p in positions:
            pos_map[(p.account_id, p.ticker)] = p

        all_keys = set(trade_agg.keys()) | set(pos_map.keys())
        matches = []
        discrepancies = []
        trade_only = []
        position_only = []

        for key in sorted(all_keys):
            account_id, ticker = key
            in_trades = key in trade_agg
            in_positions = key in pos_map

            if in_trades and not in_positions:
                trade_only.append(
                    {
                        "account_id": account_id,
                        "ticker": ticker,
                        "trade_shares": trade_agg[key],
                    }
                )
            elif in_positions and not in_trades:
                position_only.append(
                    {
                        "account_id": account_id,
                        "ticker": ticker,
                        "position_shares": pos_map[key].shares,
                        "position_market_value": pos_map[key].market_value,
                    }
                )
            else:
                trade_shares = trade_agg[key]
                pos = pos_map[key]
                share_diff = round(trade_shares - pos.shares, 6)

                entry = {
                    "account_id": account_id,
                    "ticker": ticker,
                    "trade_shares": trade_shares,
                    "position_shares": pos.shares,
                    "share_difference": share_diff,
                    "position_market_value": pos.market_value,
                }

                if share_diff != 0:
                    discrepancies.append(entry)
                else:
                    matches.append(entry)

        return {
            "date": report_date.isoformat(),
            "summary": {
                "total_entries": len(all_keys),
                "matches": len(matches),
                "discrepancies": len(discrepancies),
                "trade_only": len(trade_only),
                "position_only": len(position_only),
            },
            "discrepancies": discrepancies,
            "trade_only": trade_only,
            "position_only": position_only,
            "matches": matches,
        }
    finally:
        session.close()
