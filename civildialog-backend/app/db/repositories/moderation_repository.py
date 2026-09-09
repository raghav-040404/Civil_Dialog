from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.analysis import MessageAnalysis
from app.models.analysis_issue import AnalysisIssue
from app.models.message import Message
from app.models.rewrite_suggestion import RewriteSuggestion
from app.services.civility_service import CIVILITY_SCORE_VERSION
from app.utils.exceptions import AppException


def save_analysis(
    db: Session,
    *,
    message: Message,
    civility_score: int,
    moderation_result: dict,
) -> MessageAnalysis:
    """
    Persists the result of app.services.moderation_service.analyze_text()
    for one message: a MessageAnalysis row, its AnalysisIssue rows (from
    llm_analysis.issues), and a RewriteSuggestion row (only when the LLM
    actually flagged the text as problematic and offered a rewrite).

    Everything here is add()/flush()'d onto the caller's session — nothing
    is committed. The request-scoped session from app.db.session.get_db()
    commits once, at the very end of the request, and rolls back
    everything written here (message, analysis, issues, rewrite) if any
    later step in the request fails — so a failed analysis never leaves
    partial rows behind.

    Only num_tokens is kept from `preprocessing`; the per-token array is
    intentionally never stored (no analytical value, disproportionate
    row size). `raw_data` holds only the one piece of NLP output with no
    dedicated column: the toxic-bert per-label breakdown. Every other
    LLM/NLP field already has a column or a normalized table, so nothing
    else is duplicated into it.
    """

    toxicity = moderation_result["toxicity"]
    hate_speech = moderation_result["hate_speech"]
    sentiment = moderation_result["sentiment"]
    preprocessing = moderation_result.get("preprocessing") or {}
    llm_analysis = moderation_result.get("llm_analysis") or {}

    toxicity_labels = toxicity.get("labels")

    analysis = MessageAnalysis(
        message_id=message.id,
        civility_score=civility_score,
        score_version=CIVILITY_SCORE_VERSION,
        toxicity_score=toxicity["toxicity_score"],
        is_toxic=toxicity["is_toxic"],
        hate_speech_score=hate_speech["hate_speech_score"],
        is_hate_speech=hate_speech["is_hate_speech"],
        hate_speech_label=hate_speech.get("label"),
        sentiment=sentiment.get("sentiment"),
        sentiment_confidence=sentiment.get("confidence"),
        llm_is_problematic=llm_analysis.get("is_problematic"),
        llm_sentiment=llm_analysis.get("sentiment"),
        llm_explanation=llm_analysis.get("explanation"),
        llm_confidence=llm_analysis.get("confidence"),
        num_tokens=preprocessing.get("num_tokens"),
        raw_data={"toxicity_labels": toxicity_labels} if toxicity_labels else None,
    )

    db.add(analysis)
    db.flush()

    for issue in llm_analysis.get("issues", []):
        db.add(AnalysisIssue(
            analysis_id=analysis.id,
            issue_type=issue.get("type", "unknown"),
            severity=issue.get("severity"),
            confidence=issue.get("confidence"),
            evidence=issue.get("evidence"),
        ))

    rewrite_text = llm_analysis.get("rewrite")

    if llm_analysis.get("is_problematic") and rewrite_text:
        db.add(RewriteSuggestion(
            analysis_id=analysis.id,
            rewrite_text=rewrite_text,
            explanation=llm_analysis.get("explanation"),
            suggestions=llm_analysis.get("suggestions") or None,
        ))

    db.flush()

    return analysis


def accept_rewrite(
    db: Session,
    *,
    message_id: int,
    user_id: int,
    is_admin: bool = False,
) -> RewriteSuggestion:
    """
    Marks a message's rewrite suggestion as accepted: sets
    RewriteSuggestion.was_accepted/accepted_at and copies the rewrite
    text onto Message.final_text/was_rewritten. Everything here is a
    plain attribute mutation on ORM objects already tracked by the
    caller's session, flushed but not committed — the request-scoped
    session from app.db.session.get_db() commits once at the end of the
    request (single transaction) and rolls back all of it on failure.

    accepted_at uses the application clock (not func.now()) because it
    records the moment the accept action was processed, not a row's
    insertion time -- unlike created_at columns elsewhere in this schema,
    which intentionally use the database clock (see app/models/message.py).
    """

    message = db.get(Message, message_id)

    if message is None:
        raise AppException(
            message="Message not found.",
            code="MESSAGE_NOT_FOUND",
            status_code=404,
        )

    if message.user_id != user_id and not is_admin:
        raise AppException(
            message="This message does not belong to you.",
            code="MESSAGE_FORBIDDEN",
            status_code=403,
        )

    analysis = db.scalar(
        select(MessageAnalysis).where(MessageAnalysis.message_id == message.id)
    )

    if analysis is None:
        raise AppException(
            message="This message has not been analyzed yet.",
            code="ANALYSIS_NOT_FOUND",
            status_code=404,
        )

    rewrite = db.scalar(
        select(RewriteSuggestion)
        .where(RewriteSuggestion.analysis_id == analysis.id)
        .order_by(RewriteSuggestion.created_at.desc())
    )

    if rewrite is None:
        raise AppException(
            message="No rewrite suggestion exists for this message.",
            code="REWRITE_SUGGESTION_NOT_FOUND",
            status_code=404,
        )

    if rewrite.was_accepted:
        raise AppException(
            message="This rewrite suggestion has already been accepted.",
            code="REWRITE_ALREADY_ACCEPTED",
            status_code=409,
        )

    rewrite.was_accepted = True
    rewrite.accepted_at = datetime.now(timezone.utc)
    message.final_text = rewrite.rewrite_text
    message.was_rewritten = True

    db.flush()

    return rewrite
