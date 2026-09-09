from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.conversation import Conversation
from app.models.message import Message
from app.models.analysis import MessageAnalysis
from app.utils.exceptions import AppException


def get_or_create_conversation(
    db: Session,
    *,
    user_id: int,
    conversation_id: Optional[int],
) -> Conversation:
    """
    Resolves the conversation a new message belongs to.

    The current API has no prior concept of a conversation — the minimal,
    compatible mechanism used here: if the client passes a
    conversation_id, the message is attached to it (after checking
    ownership); if it omits one, a new conversation is started. A client
    that wants several messages in one conversation simply reuses the
    conversation_id returned by the first call. There is no implicit
    "resume my last active conversation" heuristic — that would be a
    guess this endpoint has no reliable basis for making.
    """

    if conversation_id is not None:
        conversation = db.get(Conversation, conversation_id)

        if conversation is None:
            raise AppException(
                message="Conversation not found.",
                code="CONVERSATION_NOT_FOUND",
                status_code=404,
            )

        if conversation.user_id != user_id:
            raise AppException(
                message="This conversation does not belong to you.",
                code="CONVERSATION_FORBIDDEN",
                status_code=403,
            )

        return conversation

    conversation = Conversation(user_id=user_id)
    db.add(conversation)
    db.flush()

    return conversation


def create_message(
    db: Session,
    *,
    conversation_id: int,
    user_id: int,
    original_text: str,
    final_text: Optional[str] = None,
    was_rewritten: bool = False,
) -> Message:
    message = Message(
        conversation_id=conversation_id,
        user_id=user_id,
        original_text=original_text,
        final_text=final_text,
        was_rewritten=was_rewritten,
    )

    db.add(message)
    db.flush()

    return message


def refresh_conversation_stats(db: Session, conversation: Conversation) -> None:
    """
    Recomputes conversations.message_count and avg_civility_score from
    the database via SQL aggregates, rather than accumulating them
    incrementally in Python — so the denormalized values can never drift
    from the rows that back them.
    """

    message_count = db.scalar(
        select(func.count(Message.id))
        .where(Message.conversation_id == conversation.id)
    )

    avg_score = db.scalar(
        select(func.avg(MessageAnalysis.civility_score))
        .select_from(Message)
        .join(MessageAnalysis, MessageAnalysis.message_id == Message.id)
        .where(Message.conversation_id == conversation.id)
    )

    conversation.message_count = message_count or 0
    conversation.avg_civility_score = (
        round(float(avg_score), 2) if avg_score is not None else None
    )
