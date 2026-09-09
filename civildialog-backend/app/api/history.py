from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.schemas.analytics import HistoryResponse
from app.services import analytics_service


router = APIRouter()


@router.get("/messages", response_model=HistoryResponse)
async def message_history(
    conversation_id: Optional[int] = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    The authenticated user's own message history, newest first. Always
    scoped to the caller — there is no parameter that can retrieve
    another user's messages.
    """

    data = analytics_service.get_message_history(
        db,
        user_id=current_user["id"],
        conversation_id=conversation_id,
        limit=limit,
        offset=offset,
    )

    return {"success": True, "data": data}
