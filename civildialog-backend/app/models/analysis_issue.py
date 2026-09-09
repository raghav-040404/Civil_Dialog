from typing import Optional

from sqlalchemy import BigInteger, Double, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class AnalysisIssue(Base):
    """
    ORM model for a single communication issue / logical fallacy detected
    by Member 4's LLM analysis for one message.

    One MessageAnalysis can have many AnalysisIssue rows (0..N — most
    civil messages have none).

    ``issue_type`` and ``severity`` store the raw string values of Member
    4's ``IssueType`` / ``SeverityLevel`` enums (see
    CivilDialog-AI/backend/schemas/llm_schema.py on the
    feature/llm-integration-rewrite branch — e.g. "ad_hominem",
    "strawman", "hate_speech" / "low", "medium", "high"). No CHECK
    constraint is applied here: that enum is owned by Member 4's module
    and may grow, and this table must not need a migration every time it
    does.

    Relationships
    -------------
    * ``analysis`` — many-to-one → :class:`app.models.analysis.MessageAnalysis`
    """

    __tablename__ = "analysis_issues"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    # ON DELETE CASCADE: issues have no meaning once their parent analysis
    # is gone. Indexed because every issue is looked up by its analysis
    # (fetch-all-issues-for-analysis) and analytics group issues by type
    # across many analyses (analysis_id used as the join key).
    analysis_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("message_analyses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    issue_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    severity: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )

    confidence: Mapped[Optional[float]] = mapped_column(
        Double,
        nullable=True,
    )

    evidence: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------
    analysis = relationship(
        "MessageAnalysis",
        back_populates="issues",
        lazy="select",
    )
