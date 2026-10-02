import os

import pytest
from sqlalchemy import create_engine, text


@pytest.fixture(scope="session")
def test_database_url() -> str:
    return os.getenv(
        "TEST_DATABASE_URL",
        "postgresql+psycopg://app:app@localhost:5432/eve_healthcare_test",
    )


@pytest.fixture(scope="session")
def test_engine(test_database_url: str):
    engine = create_engine(test_database_url, pool_pre_ping=True)
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception as exc:
        engine.dispose()
        pytest.skip(f"test database unavailable: {exc}")
    yield engine
    engine.dispose()