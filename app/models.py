from datetime import date

from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Trade(Base):
    __tablename__ = "trades"

    id: Mapped[int] = mapped_column(primary_key=True)
    trade_date: Mapped[date]
    account_id: Mapped[str] = mapped_column(String(20))
    ticker: Mapped[str] = mapped_column(String(10))
    quantity: Mapped[float]
    price: Mapped[float | None] = mapped_column(default=None)
    market_value: Mapped[float | None] = mapped_column(default=None)
    trade_type: Mapped[str | None] = mapped_column(String(10), default=None)
    settlement_date: Mapped[date | None] = mapped_column(default=None)
    source_system: Mapped[str | None] = mapped_column(String(50), default=None)
    source_file: Mapped[str | None] = mapped_column(String(255), default=None)

    __table_args__ = (
        UniqueConstraint(
            "trade_date",
            "account_id",
            "ticker",
            "source_file",
            name="uq_trade",
        ),
    )


class Position(Base):
    __tablename__ = "positions"

    id: Mapped[int] = mapped_column(primary_key=True)
    report_date: Mapped[date]
    account_id: Mapped[str] = mapped_column(String(20))
    ticker: Mapped[str] = mapped_column(String(10))
    shares: Mapped[float]
    market_value: Mapped[float]
    custodian_ref: Mapped[str] = mapped_column(String(50))

    __table_args__ = (
        UniqueConstraint(
            "report_date",
            "account_id",
            "ticker",
            name="uq_position",
        ),
    )
