import os

import pytest

from app import create_app
from app.ingestion import parse_positions_yaml, parse_trade_csv, parse_trade_pipe


@pytest.fixture()
def app():
    application = create_app(config={"DATABASE_URL": "sqlite://"})
    yield application


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def loaded_client(client):
    """Client with all sample data pre-loaded."""
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")

    with open(os.path.join(data_dir, "trades_format1.csv")) as f:
        parse_trade_csv(f.read(), "trades_format1.csv")

    with open(os.path.join(data_dir, "trades_format2.txt")) as f:
        parse_trade_pipe(f.read(), "trades_format2.txt")

    with open(os.path.join(data_dir, "positions.yaml")) as f:
        parse_positions_yaml(f.read(), "positions.yaml")

    return client
