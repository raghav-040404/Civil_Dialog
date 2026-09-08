from fastapi import APIRouter

from app.schemas.moderation import (
    ModerationRequest,
    ModerationResponse
)

from app.services.moderation_service import analyze_text


router = APIRouter()


@router.post(
    "/analyze",
    response_model=ModerationResponse
)
async def analyze_message(request: ModerationRequest):

    result = await analyze_text(request.text)

    return {
        "success": True,
        "data": result
    }