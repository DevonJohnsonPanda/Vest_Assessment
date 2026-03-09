from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session

engine: Engine | None = None


class Base(DeclarativeBase):
    pass


def init_db(database_url: str = "sqlite:///clearinghouse.db") -> None:
    global engine
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)


def get_session() -> Session:
    return Session(engine)
