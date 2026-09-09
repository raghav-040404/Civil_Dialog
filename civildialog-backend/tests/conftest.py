"""
Shared pytest fixtures for database-backed tests.

Requires a running PostgreSQL instance reachable at DATABASE_URL (see
docker-compose.yml: `docker compose up -d`) and Alembic migrations applied
(`alembic upgrade head`).

`db_session` wraps every test in an outer transaction that is always
rolled back, using a SAVEPOINT so that even code under test which calls
db.commit() (e.g. app/db/repositories/user_repository.py, which opens its
own SessionLocal()) does not leak rows into the real development database
long-term. Code that opens its own session on a *different* connection is
not covered by this SAVEPOINT — see tests/test_persistence.py for how
those are cleaned up explicitly.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from sqlalchemy import event
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.database import engine as app_engine


@pytest.fixture
def db_session():
    connection = app_engine.connect()
    outer_transaction = connection.begin()

    TestingSessionLocal = sessionmaker(bind=connection, expire_on_commit=False)
    session = TestingSessionLocal()

    nested = connection.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def _restart_savepoint(sess, trans):
        nonlocal nested
        if not nested.is_active:
            nested = connection.begin_nested()

    try:
        yield session
    finally:
        session.close()
        if outer_transaction.is_active:
            outer_transaction.rollback()
        connection.close()
