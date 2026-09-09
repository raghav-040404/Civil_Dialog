from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Conversation(Base):
    """
    ORM model for a conversation session within CivilDialog.

    Each conversation belongs to a single user and tracks an ongoing
    dialogue.  The ``message_count`` and ``avg_civility_score`` fields
    are denormalised counters / aggregates that will be maintained by
    application code when messages and their analyses are persisted in
    later phases.

    Relationships
    -------------
    * ``user`` — many-to-one back-reference to :class:`app.models.user.User`.
    """

    __tablename__ = "conversations"

    # ------------------------------------------------------------------
    # Primary key
    # ------------------------------------------------------------------
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    # ------------------------------------------------------------------
    # Foreign key → users.id
    # ------------------------------------------------------------------
    # Indexed because conversations are almost always queried per-user.
    # ON DELETE CASCADE: if a user is removed, their conversations are
    # removed as well (data-ownership semantics).
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ------------------------------------------------------------------
    # Descriptive fields
    # ------------------------------------------------------------------
    title: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="active",
        server_default="active",
    )

    # ------------------------------------------------------------------
    # Denormalised aggregates — updated by application code in later
    # phases when messages / analyses are persisted.
    # ------------------------------------------------------------------
    message_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    # NUMERIC(5,2) allows scores from 0.00 to 999.99 — more than
    # sufficient for a 0-100 civility scale.
    avg_civility_score: Mapped[Optional[float]] = mapped_column(
        Numeric(precision=5, scale=2),
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Timestamps
    # ------------------------------------------------------------------
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    ended_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------
    user = relationship(
        "User",
        back_populates="conversations",
        lazy="select",
    )

    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        lazy="select",
    )

