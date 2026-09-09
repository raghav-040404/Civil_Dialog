from typing import Optional

from sqlalchemy.orm import Session

from app.services.nlp_service import analyze_nlp
from app.services.llm_service import analyze_with_llm
from app.services.civility_service import calculate_civility_score
from app.db.repositories.message_repository import (
    create_message,
    get_or_create_conversation,
    refresh_conversation_stats,
)
from app.db.repositories.moderation_repository import save_analysis
from app.utils.exceptions import AppException


async def analyze_text(text: str) -> dict:

    cleaned_text = text.strip()

    if not cleaned_text:
        raise AppException(
            message="Text cannot be empty.",
            code="EMPTY_TEXT",
            status_code=400
        )

    nlp_result = await analyze_nlp(cleaned_text)

    llm_result = await analyze_with_llm(cleaned_text)

    civility_score = calculate_civility_score(
        toxicity_score=nlp_result["toxicity"]["toxicity_score"],
        hate_speech_score=nlp_result["hate_speech"]["hate_speech_score"]
    )

    return {
        "text": cleaned_text,
        **nlp_result,
        **llm_result,
        "civility_score": civility_score
    }


async def analyze_and_persist(
    db: Session,
    *,
    user_id: int,
    conversation_id: Optional[int],
    text: str
) -> dict:
    """
    Runs the existing analyze_text() pipeline unchanged, then persists the
    result as Message / MessageAnalysis / AnalysisIssue / RewriteSuggestion
    rows within the caller's database transaction (see
    app/db/session.py:get_db — it commits once at the end of the request
    and rolls back everything on any failure).

    analyze_text() itself stays free of any database concern; this is the
    thin, separate layer that adds persistence around it.
    """

    result = await analyze_text(text)

    conversation = get_or_create_conversation(
        db,
        user_id=user_id,
        conversation_id=conversation_id
    )

    message = create_message(
        db,
        conversation_id=conversation.id,
        user_id=user_id,
        original_text=result["text"]
    )

    save_analysis(
        db,
        message=message,
        civility_score=result["civility_score"],
        moderation_result=result
    )

    refresh_conversation_stats(db, conversation)

    return {
        **result,
        "conversation_id": conversation.id,
        "message_id": message.id
    }