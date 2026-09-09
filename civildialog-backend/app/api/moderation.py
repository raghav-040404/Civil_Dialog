from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db

from app.schemas.moderation import (
    ModerationRequest,
    ModerationResponse
)

from app.services.moderation_service import analyze_and_persist


router = APIRouter()


@router.post(
    "/analyze",
    response_model=ModerationResponse
)
async def analyze_message(
    request: ModerationRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    result = await analyze_and_persist(
        db,
        user_id=current_user["id"],
        conversation_id=request.conversation_id,
        text=request.text
    )

    return {
        "success": True,
        "data": result
    }
