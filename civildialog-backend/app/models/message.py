from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Index, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Message(Base):
    """
    ORM model for an individual message within a CivilDialog conversation.

    Each message belongs to exactly one conversation and one user.  The
    ``user_id`` foreign key is intentionally denormalised (it could be
    derived from ``conversation.user_id``) because analytics and history
    queries frequently filter or aggregate messages by user, and the
    extra column avoids an expensive join on every such query.

    Relationships
    -------------
    * ``conversation`` — many-to-one → :class:`app.models.conversation.Conversation`
    * ``user``         — many-to-one → :class:`app.models.user.User`
    """

    __tablename__ = "messages"

    # Composite index backing GET /api/v1/history/messages
    # (app/services/analytics_service.py:get_message_history), which always
    # filters WHERE user_id = ? and sorts ORDER BY created_at DESC — the
    # single-column index on user_id alone would still require an in-memory
    # sort of every one of that user's messages on each page request.
    __table_args__ = (
        Index("ix_messages_user_id_created_at", "user_id", "created_at"),
    )

    # ------------------------------------------------------------------
    # Primary key
    # ------------------------------------------------------------------
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    # ------------------------------------------------------------------
    # Foreign keys
    # ------------------------------------------------------------------
    # ON DELETE CASCADE on both: deleting a conversation or user removes
    # the associated messages (data-ownership semantics, consistent with
    # conversations.user_id → users.id).
    conversation_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ------------------------------------------------------------------
    # Message content
    # ------------------------------------------------------------------
    original_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    final_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    was_rewritten: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
    )

    # ------------------------------------------------------------------
    # Timestamps
    # ------------------------------------------------------------------
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------
    conversation = relationship(
        "Conversation",
        back_populates="messages",
        lazy="select",
    )

    user = relationship(
        "User",
        back_populates="messages",
        lazy="select",
    )

    analysis = relationship(
        "MessageAnalysis",
        back_populates="message",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="select",
    )

