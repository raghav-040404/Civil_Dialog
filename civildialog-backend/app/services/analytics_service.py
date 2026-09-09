"""
Analytics queries against PostgreSQL.

Every function here issues SQL aggregates (COUNT / AVG / GROUP BY / date
grouping) rather than loading rows into Python and computing there — see
app/models/*.py for the indexes these queries rely on
(messages.user_id, messages.conversation_id, messages.created_at,
message_analyses.civility_score, message_analyses.analyzed_at,
message_analyses.message_id, analysis_issues.analysis_id,
rewrite_suggestions.analysis_id — all already created by the Phase B
migrations; see the report for why no further indexes were added).

Scope convention used throughout (see final report for the reasoning):
  * user_id=None  -> platform-wide (admin-only endpoints)
  * user_id=<int> -> a single user's own data
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import and_, case, func, select
from sqlalchemy.orm import Session

from app.models.analysis_issue import AnalysisIssue
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.analysis import MessageAnalysis
from app.models.rewrite_suggestion import RewriteSuggestion
from app.models.user import User


def _analysis_query_base(user_id: Optional[int]):
    """
    Base SELECT ... FROM message_analyses JOIN messages, optionally
    scoped to one user. Shared by every function that aggregates over
    message_analyses so the join/filter logic is defined once.
    """
    stmt = select(MessageAnalysis).select_from(MessageAnalysis).join(
        Message, Message.id == MessageAnalysis.message_id
    )
    if user_id is not None:
        stmt = stmt.where(Message.user_id == user_id)
    return stmt


def _date_filters(
    column,
    date_from: Optional[datetime],
    date_to: Optional[datetime],
) -> list:
    conditions = []
    if date_from is not None:
        conditions.append(column >= date_from)
    if date_to is not None:
        conditions.append(column <= date_to)
    return conditions


# ---------------------------------------------------------------------
# 1. Overview
# ---------------------------------------------------------------------
def get_overview(db: Session) -> dict:
    total_users = db.scalar(select(func.count(User.id))) or 0
    total_conversations = db.scalar(select(func.count(Conversation.id))) or 0
    total_messages = db.scalar(select(func.count(Message.id))) or 0

    total_analyses = db.scalar(select(func.count(MessageAnalysis.id))) or 0
    avg_civility = db.scalar(select(func.avg(MessageAnalysis.civility_score)))
    toxic_count = db.scalar(
        select(func.count()).select_from(MessageAnalysis).where(MessageAnalysis.is_toxic.is_(True))
    ) or 0
    hate_count = db.scalar(
        select(func.count()).select_from(MessageAnalysis).where(MessageAnalysis.is_hate_speech.is_(True))
    ) or 0

    total_rewrites = db.scalar(select(func.count(RewriteSuggestion.id))) or 0
    accepted_rewrites = db.scalar(
        select(func.count()).select_from(RewriteSuggestion).where(RewriteSuggestion.was_accepted.is_(True))
    ) or 0

    return {
        "total_users": total_users,
        "total_conversations": total_conversations,
        "total_messages": total_messages,
        "avg_civility_score": round(float(avg_civility), 2) if avg_civility is not None else None,
        "toxic_message_count": toxic_count,
        "toxic_message_rate": round(toxic_count / total_analyses, 4) if total_analyses else 0.0,
        "hate_speech_count": hate_count,
        "hate_speech_rate": round(hate_count / total_analyses, 4) if total_analyses else 0.0,
        "rewrite_offered_count": total_rewrites,
        "rewrite_accepted_count": accepted_rewrites,
        "rewrite_adoption_rate": round(accepted_rewrites / total_rewrites, 4) if total_rewrites else 0.0,
    }


# ---------------------------------------------------------------------
# 2. Civility trend
# ---------------------------------------------------------------------
def get_civility_trend(
    db: Session,
    *,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    granularity: str = "day",
    user_id: Optional[int] = None,
) -> list[dict]:
    granularity = granularity if granularity in ("day", "week", "month") else "day"

    period = func.date_trunc(granularity, MessageAnalysis.analyzed_at)

    stmt = (
        select(
            period.label("period"),
            func.count(MessageAnalysis.id).label("message_count"),
            func.avg(MessageAnalysis.civility_score).label("avg_civility_score"),
        )
        .select_from(MessageAnalysis)
        .join(Message, Message.id == MessageAnalysis.message_id)
    )

    conditions = _date_filters(MessageAnalysis.analyzed_at, date_from, date_to)
    if user_id is not None:
        conditions.append(Message.user_id == user_id)
    if conditions:
        stmt = stmt.where(and_(*conditions))

    stmt = stmt.group_by(period).order_by(period)

    return [
        {
            "date": row.period.date().isoformat(),
            "message_count": row.message_count,
            "avg_civility_score": round(float(row.avg_civility_score), 2) if row.avg_civility_score is not None else None,
        }
        for row in db.execute(stmt).all()
    ]


# ---------------------------------------------------------------------
# 3. Civility distribution
# ---------------------------------------------------------------------
_DISTRIBUTION_BUCKETS = ["0-20", "21-40", "41-60", "61-80", "81-100"]


def get_civility_distribution(
    db: Session,
    *,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    user_id: Optional[int] = None,
) -> list[dict]:
    bucket = case(
        (MessageAnalysis.civility_score <= 20, "0-20"),
        (MessageAnalysis.civility_score <= 40, "21-40"),
        (MessageAnalysis.civility_score <= 60, "41-60"),
        (MessageAnalysis.civility_score <= 80, "61-80"),
        else_="81-100",
    ).label("bucket")

    stmt = (
        select(bucket, func.count(MessageAnalysis.id))
        .select_from(MessageAnalysis)
        .join(Message, Message.id == MessageAnalysis.message_id)
    )

    conditions = _date_filters(MessageAnalysis.analyzed_at, date_from, date_to)
    if user_id is not None:
        conditions.append(Message.user_id == user_id)
    if conditions:
        stmt = stmt.where(and_(*conditions))

    stmt = stmt.group_by(bucket)

    counts = dict(db.execute(stmt).all())
    total = sum(counts.values())

    return [
        {
            "range": b,
            "count": counts.get(b, 0),
            "percentage": round(counts.get(b, 0) / total * 100, 2) if total else 0.0,
        }
        for b in _DISTRIBUTION_BUCKETS
    ]


# ---------------------------------------------------------------------
# 4. Per-user summary
# ---------------------------------------------------------------------
def get_user_summary(db: Session, user_id: int) -> dict:
    message_count = db.scalar(
        select(func.count(Message.id)).where(Message.user_id == user_id)
    ) or 0

    conversation_count = db.scalar(
        select(func.count(Conversation.id)).where(Conversation.user_id == user_id)
    ) or 0

    base = _analysis_query_base(user_id).subquery()

    avg_civility = db.scalar(select(func.avg(base.c.civility_score)))
    toxic_count = db.scalar(
        select(func.count()).select_from(base).where(base.c.is_toxic.is_(True))
    ) or 0
    hate_count = db.scalar(
        select(func.count()).select_from(base).where(base.c.is_hate_speech.is_(True))
    ) or 0

    rewrite_count = db.scalar(
        select(func.count(RewriteSuggestion.id))
        .select_from(RewriteSuggestion)
        .join(MessageAnalysis, MessageAnalysis.id == RewriteSuggestion.analysis_id)
        .join(Message, Message.id == MessageAnalysis.message_id)
        .where(Message.user_id == user_id)
    ) or 0

    accepted_rewrite_count = db.scalar(
        select(func.count(RewriteSuggestion.id))
        .select_from(RewriteSuggestion)
        .join(MessageAnalysis, MessageAnalysis.id == RewriteSuggestion.analysis_id)
        .join(Message, Message.id == MessageAnalysis.message_id)
        .where(Message.user_id == user_id, RewriteSuggestion.was_accepted.is_(True))
    ) or 0

    return {
        "user_id": user_id,
        "message_count": message_count,
        "conversation_count": conversation_count,
        "avg_civility_score": round(float(avg_civility), 2) if avg_civility is not None else None,
        "toxic_count": toxic_count,
        "hate_speech_count": hate_count,
        "rewrite_count": rewrite_count,
        "accepted_rewrite_count": accepted_rewrite_count,
    }


# ---------------------------------------------------------------------
# 5. Per-conversation summary
# ---------------------------------------------------------------------
def get_conversation_summary(db: Session, conversation_id: int) -> dict:
    message_count = db.scalar(
        select(func.count(Message.id)).where(Message.conversation_id == conversation_id)
    ) or 0

    joined = (
        select(MessageAnalysis)
        .select_from(MessageAnalysis)
        .join(Message, Message.id == MessageAnalysis.message_id)
        .where(Message.conversation_id == conversation_id)
        .subquery()
    )

    avg_civility = db.scalar(select(func.avg(joined.c.civility_score)))
    toxic_count = db.scalar(
        select(func.count()).select_from(joined).where(joined.c.is_toxic.is_(True))
    ) or 0
    hate_count = db.scalar(
        select(func.count()).select_from(joined).where(joined.c.is_hate_speech.is_(True))
    ) or 0

    sentiment_rows = db.execute(
        select(joined.c.sentiment, func.count())
        .select_from(joined)
        .group_by(joined.c.sentiment)
    ).all()
    sentiment_distribution = {row[0] or "UNKNOWN": row[1] for row in sentiment_rows}

    rewrite_count = db.scalar(
        select(func.count(RewriteSuggestion.id))
        .select_from(RewriteSuggestion)
        .join(MessageAnalysis, MessageAnalysis.id == RewriteSuggestion.analysis_id)
        .join(Message, Message.id == MessageAnalysis.message_id)
        .where(Message.conversation_id == conversation_id)
    ) or 0

    return {
        "conversation_id": conversation_id,
        "message_count": message_count,
        "avg_civility_score": round(float(avg_civility), 2) if avg_civility is not None else None,
        "toxic_count": toxic_count,
        "hate_speech_count": hate_count,
        "sentiment_distribution": sentiment_distribution,
        "rewrite_count": rewrite_count,
    }


# ---------------------------------------------------------------------
# 6. Issue distribution
# ---------------------------------------------------------------------
def get_issue_distribution(
    db: Session,
    *,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    user_id: Optional[int] = None,
    limit: int = 10,
) -> list[dict]:
    stmt = (
        select(AnalysisIssue.issue_type, func.count(AnalysisIssue.id))
        .select_from(AnalysisIssue)
        .join(MessageAnalysis, MessageAnalysis.id == AnalysisIssue.analysis_id)
        .join(Message, Message.id == MessageAnalysis.message_id)
    )

    conditions = _date_filters(MessageAnalysis.analyzed_at, date_from, date_to)
    if user_id is not None:
        conditions.append(Message.user_id == user_id)
    if conditions:
        stmt = stmt.where(and_(*conditions))

    stmt = (
        stmt.group_by(AnalysisIssue.issue_type)
        .order_by(func.count(AnalysisIssue.id).desc())
        .limit(limit)
    )

    rows = db.execute(stmt).all()
    total = sum(r[1] for r in rows)

    return [
        {
            "issue_type": issue_type,
            "count": count,
            "percentage": round(count / total * 100, 2) if total else 0.0,
        }
        for issue_type, count in rows
    ]


# ---------------------------------------------------------------------
# 7. Rewrite adoption
# ---------------------------------------------------------------------
def get_rewrite_adoption(
    db: Session,
    *,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    user_id: Optional[int] = None,
) -> dict:
    stmt = (
        select(RewriteSuggestion)
        .select_from(RewriteSuggestion)
        .join(MessageAnalysis, MessageAnalysis.id == RewriteSuggestion.analysis_id)
        .join(Message, Message.id == MessageAnalysis.message_id)
    )

    conditions = _date_filters(RewriteSuggestion.created_at, date_from, date_to)
    if user_id is not None:
        conditions.append(Message.user_id == user_id)

    base = (stmt.where(and_(*conditions)) if conditions else stmt).subquery()

    total = db.scalar(select(func.count()).select_from(base)) or 0
    accepted = db.scalar(
        select(func.count()).select_from(base).where(base.c.was_accepted.is_(True))
    ) or 0
    rejected = db.scalar(
        select(func.count()).select_from(base).where(base.c.was_accepted.is_(False))
    ) or 0

    return {
        "total_suggestions": total,
        "accepted": accepted,
        "rejected": rejected,
        "adoption_percentage": round(accepted / total * 100, 2) if total else 0.0,
    }


# ---------------------------------------------------------------------
# 8. Message history
# ---------------------------------------------------------------------
def get_message_history(
    db: Session,
    *,
    user_id: int,
    conversation_id: Optional[int] = None,
    limit: int = 20,
    offset: int = 0,
) -> dict:
    conditions = [Message.user_id == user_id]
    if conversation_id is not None:
        conditions.append(Message.conversation_id == conversation_id)

    total = db.scalar(
        select(func.count(Message.id)).where(and_(*conditions))
    ) or 0

    stmt = (
        select(Message, MessageAnalysis)
        .select_from(Message)
        .outerjoin(MessageAnalysis, MessageAnalysis.message_id == Message.id)
        .where(and_(*conditions))
        # Secondary sort on id: PostgreSQL's now() is the *transaction*
        # start time, so two messages created in the same transaction can
        # get an identical created_at. id (monotonic) breaks the tie
        # deterministically in insertion order.
        .order_by(Message.created_at.desc(), Message.id.desc())
        .limit(limit)
        .offset(offset)
    )

    items = []
    for message, analysis in db.execute(stmt).all():
        items.append({
            "message_id": message.id,
            "conversation_id": message.conversation_id,
            "original_text": message.original_text,
            "final_text": message.final_text,
            "was_rewritten": message.was_rewritten,
            "created_at": message.created_at.isoformat(),
            "civility_score": float(analysis.civility_score) if analysis else None,
            "is_toxic": analysis.is_toxic if analysis else None,
            "is_hate_speech": analysis.is_hate_speech if analysis else None,
            "sentiment": analysis.sentiment if analysis else None,
        })

    return {"total": total, "limit": limit, "offset": offset, "items": items}


# ---------------------------------------------------------------------
# 9. Daily report (used by the CSV export)
# ---------------------------------------------------------------------
def get_daily_report(
    db: Session,
    *,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    user_id: Optional[int] = None,
) -> list[dict]:
    period = func.date_trunc("day", MessageAnalysis.analyzed_at)

    stmt = (
        select(
            period.label("period"),
            func.count(MessageAnalysis.id).label("message_count"),
            func.avg(MessageAnalysis.civility_score).label("avg_civility_score"),
            func.count().filter(MessageAnalysis.is_toxic.is_(True)).label("toxic_count"),
            func.count().filter(MessageAnalysis.is_hate_speech.is_(True)).label("hate_speech_count"),
        )
        .select_from(MessageAnalysis)
        .join(Message, Message.id == MessageAnalysis.message_id)
    )

    conditions = _date_filters(MessageAnalysis.analyzed_at, date_from, date_to)
    if user_id is not None:
        conditions.append(Message.user_id == user_id)
    if conditions:
        stmt = stmt.where(and_(*conditions))

    stmt = stmt.group_by(period).order_by(period)

    rewrite_stmt = (
        select(
            func.date_trunc("day", RewriteSuggestion.created_at).label("period"),
            func.count(RewriteSuggestion.id).label("rewrite_count"),
        )
        .select_from(RewriteSuggestion)
        .join(MessageAnalysis, MessageAnalysis.id == RewriteSuggestion.analysis_id)
        .join(Message, Message.id == MessageAnalysis.message_id)
    )
    rewrite_conditions = _date_filters(RewriteSuggestion.created_at, date_from, date_to)
    if user_id is not None:
        rewrite_conditions.append(Message.user_id == user_id)
    if rewrite_conditions:
        rewrite_stmt = rewrite_stmt.where(and_(*rewrite_conditions))
    rewrite_stmt = rewrite_stmt.group_by("period")

    rewrite_counts = {
        row.period.date(): row.rewrite_count
        for row in db.execute(rewrite_stmt).all()
    }

    rows = []
    for row in db.execute(stmt).all():
        day = row.period.date()
        message_count = row.message_count
        rows.append({
            "date": day.isoformat(),
            "message_count": message_count,
            "avg_civility_score": round(float(row.avg_civility_score), 2) if row.avg_civility_score is not None else None,
            "toxic_count": row.toxic_count,
            "toxic_rate": round(row.toxic_count / message_count, 4) if message_count else 0.0,
            "hate_speech_count": row.hate_speech_count,
            "hate_speech_rate": round(row.hate_speech_count / message_count, 4) if message_count else 0.0,
            "rewrite_count": rewrite_counts.get(day, 0),
        })

    return rows
