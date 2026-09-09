from datetime import datetime

from sqlalchemy import BigInteger, Boolean, CheckConstraint, DateTime, String, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class User(Base):
    """
    ORM model for registered CivilDialog users.

    Field set mirrors the in-memory user dict currently produced by
    app/db/repositories/user_repository.py (id, name, email, password_hash,
    role) so the repository can later be backed by this table without
    changing the shape consumed by app/services/auth_service.py,
    app/core/dependencies.py, and app/api/users.py — all of which read users
    via dict-style subscripting (e.g. current_user["role"]).
    """

    __tablename__ = "users"

    __table_args__ = (
        CheckConstraint(
            "role IN ('user', 'admin')",
            name="ck_users_role"
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    # Unique + indexed: every lookup in user_repository.py
    # (find_user_by_email) and the login flow (OAuth2PasswordRequestForm
    # username) queries by email.
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    # Matches create_user()'s existing default of role="user" and the
    # string comparison in app/core/dependencies.py:require_admin
    # (current_user["role"] != "admin").
    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="user",
        server_default="user"
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("true")
    )

    # Populated by the database (not the application clock) so that
    # timestamps stay consistent regardless of which host inserts the row.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    # Refreshed by SQLAlchemy on every ORM-level UPDATE, and defaulted by
    # the database on INSERT. Note: this does not fire for updates made
    # outside the ORM (raw SQL / another client) — see report for details.
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------
    conversations = relationship(
        "Conversation",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select",
    )

    messages = relationship(
        "Message",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select",
    )


