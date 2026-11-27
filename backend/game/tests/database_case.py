import os
from pathlib import Path
import unittest
from uuid import uuid4

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from sqlalchemy.schema import CreateSchema, DropSchema


class DatabaseTestCase(unittest.TestCase):
    def setUp(self) -> None:
        url = os.getenv("TEST_DATABASE_URL")
        if not url:
            self.skipTest("Set TEST_DATABASE_URL to run PostgreSQL tests")
        engine = create_engine(url)
        self.addCleanup(engine.dispose)
        connection = engine.connect()
        self.addCleanup(connection.close)
        schema = "test_" + uuid4().hex
        connection.execute(CreateSchema(schema))
        connection.commit()

        def drop_schema() -> None:
            connection.rollback()
            connection.execute(text("SET search_path TO public"))
            connection.execute(DropSchema(schema, cascade=True))
            connection.commit()

        self.addCleanup(drop_schema)
        connection.execute(text(f'SET search_path TO "{schema}"'))
        connection.commit()
        config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
        config.attributes["connection"] = connection
        command.upgrade(config, "head")
        self.session = Session(bind=connection)
        self.addCleanup(self.session.close)
