from collections.abc import Generator

from sqlalchemy.orm import Session

from app.db.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session.

    The session is committed if the request handler finishes
    without raising, rolled back if it does, and always closed.

    Usage:
        @router.get("/example")
        async def example(db: Session = Depends(get_db)):
            ...
    """

    db = SessionLocal()

    try:
        yield db
        db.commit()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()
