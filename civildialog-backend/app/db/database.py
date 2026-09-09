from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    """
    Declarative base for every ORM model in the project.

    All models must inherit from this class so that
    ``Base.metadata`` stays the single source of truth
    for Alembic autogeneration.
    """


engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    future=True
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False
)
