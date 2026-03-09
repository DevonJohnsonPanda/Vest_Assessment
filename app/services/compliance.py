from datetime import date

from sqlalchemy import select

from app.database import get_session
from app.models import Position


def check_concentration(report_date: date) -> list[dict]:
    """Find positions exceeding 20% concentration within their account."""
    session = get_session()
    try:
        positions = (
            session.execute(select(Position).where(Position.report_date == report_date))
            .scalars()
            .all()
        )

        accounts: dict[str, list] = {}
        for pos in positions:
            accounts.setdefault(pos.account_id, []).append(pos)

        violations = []
        for account_id, holdings in accounts.items():
            total_value = sum(abs(h.market_value) for h in holdings)
            if total_value == 0:
                continue
            for h in holdings:
                pct = abs(h.market_value) / total_value * 100
                if pct > 20:
                    violations.append(
                        {
                            "account_id": account_id,
                            "ticker": h.ticker,
                            "market_value": h.market_value,
                            "account_total": round(total_value, 2),
                            "concentration_pct": round(pct, 2),
                            "threshold": 20.0,
                            "breach_amount": round(
                                h.market_value - total_value * 0.20, 2
                            ),
                        }
                    )

        return violations
    finally:
        session.close()
