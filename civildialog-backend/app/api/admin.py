from fastapi import APIRouter, Depends

from app.core.dependencies import require_admin


router = APIRouter()


@router.get("/test")
async def admin_test(
    current_user: dict = Depends(require_admin)
):

    return {
        "success": True,
        "data": {
            "message": "Admin access granted."
        }
    }