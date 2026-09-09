from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class RewriteSuggestion(Base):
    """
    ORM model for a civil rewrite suggestion produced by Member 4's LLM
    service for one message analysis.

    Maps directly onto Member 4's ``AnalyzeResponse`` /
    ``RewriteResponse`` schemas (see
    CivilDialog-AI/backend/schemas/llm_schema.py on the
    feature/llm-integration-rewrite branch): ``rewrite`` -> rewrite_text,
    ``explanation`` -> explanation, ``suggestions`` -> suggestions,
    ``original_intent_preserved`` -> intent_preserved. No additional
    fields were introduced beyond what that output already provides.

    ``was_accepted`` / ``accepted_at`` are not populated by any current
    LLM/backend field — they exist so a future frontend action ("use this
    rewrite") can be recorded, which is the single most important signal
    for the rewrite-adoption analytics endpoint. They start out NULL /
    NULL and are set only when that frontend action happens.

    Relationships
    -------------
    * ``analysis`` — many-to-one → :class:`app.models.analysis.MessageAnalysis`
    """

    __tablename__ = "rewrite_suggestions"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    # ON DELETE CASCADE: a suggestion has no meaning without its parent
    # analysis. Indexed for the same reason as analysis_issues.analysis_id
    # — per-analysis lookups and cross-analysis aggregation both join on it.
    analysis_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("message_analyses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    rewrite_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    explanation: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # List[str] of constructive suggestions. Genuinely unmodeled/variable
    # shaped data (no per-item structure worth separate columns) — a
    # legitimate JSONB use, and not duplicated anywhere else.
    suggestions: Mapped[Optional[list]] = mapped_column(
        JSONB,
        nullable=True,
    )

    intent_preserved: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True,
    )

    was_accepted: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True,
    )

    accepted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------
    analysis = relationship(
        "MessageAnalysis",
        back_populates="rewrite_suggestions",
        lazy="select",
    )
