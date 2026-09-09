from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class MessageAnalysis(Base):
    """
    ORM model for detailed analysis of a message within CivilDialog.

    Stores NLP moderation outputs (toxicity, hate speech, sentiment),
    LLM analysis outputs, token counts, raw response payloads, and the
    calculated Civility Score (0–100 scale).

    Relationships
    -------------
    * ``message`` — one-to-one → :class:`app.models.message.Message`
    """

    __tablename__ = "message_analyses"

    # ------------------------------------------------------------------
    # Primary key
    # ------------------------------------------------------------------
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    # ------------------------------------------------------------------
    # Foreign key (1-to-1 with messages)
    # ------------------------------------------------------------------
    message_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("messages.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    # ------------------------------------------------------------------
    # Civility score & formula version
    # ------------------------------------------------------------------
    civility_score: Mapped[float] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        index=True,
    )

    score_version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="1.0.0",
        server_default="1.0.0",
    )

    # ------------------------------------------------------------------
    # NLP / Moderation scores
    # ------------------------------------------------------------------
    toxicity_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    is_toxic: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    hate_speech_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    is_hate_speech: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    hate_speech_label: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    sentiment: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )

    sentiment_confidence: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    # ------------------------------------------------------------------
    # LLM analysis fields
    # ------------------------------------------------------------------
    llm_is_problematic: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True,
    )

    llm_sentiment: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )

    llm_explanation: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    llm_confidence: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Metadata & raw data
    # ------------------------------------------------------------------
    num_tokens: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    analyzed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )

    raw_data: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------
    message = relationship(
        "Message",
        back_populates="analysis",
        lazy="select",
    )

    issues = relationship(
        "AnalysisIssue",
        back_populates="analysis",
        cascade="all, delete-orphan",
        lazy="select",
    )

    rewrite_suggestions = relationship(
        "RewriteSuggestion",
        back_populates="analysis",
        cascade="all, delete-orphan",
        lazy="select",
    )