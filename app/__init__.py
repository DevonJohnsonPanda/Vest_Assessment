from flask import Flask

from app.database import init_db


def create_app(config: dict[str, str] | None = None) -> Flask:
    app = Flask(__name__)

    database_url = "sqlite:///clearinghouse.db"
    if config and "DATABASE_URL" in config:
        database_url = config["DATABASE_URL"]

    from app import (
        models as _models,  # noqa: F401 - ensure models are registered before creating tables
    )

    init_db(database_url)

    from app.routes import compliance, ingest, positions, reconciliation

    app.register_blueprint(ingest.bp)
    app.register_blueprint(positions.bp)
    app.register_blueprint(compliance.bp)
    app.register_blueprint(reconciliation.bp)

    return app
