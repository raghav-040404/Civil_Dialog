from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.db.repositories.moderation_repository import accept_rewrite
from app.schemas.messages import AcceptRewriteResponse


router = APIRouter()


@router.post(
    "/{message_id}/accept-rewrite",
    response_model=AcceptRewriteResponse,
)
async def accept_rewrite_suggestion(
    message_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Marks the rewrite suggestion for one of the caller's own messages as
    accepted. A regular user may only act on their own messages; an admin
    (same convention as app.core.dependencies.require_admin) may act on
    any message.
    """

    rewrite = accept_rewrite(
        db,
        message_id=message_id,
        user_id=current_user["id"],
        is_admin=current_user["role"] == "admin",
    )

    return {
        "success": True,
        "data": {
            "message_id": message_id,
            "rewrite_suggestion_id": rewrite.id,
            "final_text": rewrite.rewrite_text,
            "was_rewritten": True,
            "was_accepted": rewrite.was_accepted,
            "accepted_at": rewrite.accepted_at.isoformat(),
        }
    }
