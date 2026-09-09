import csv
import io
from datetime import date, datetime, time, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, require_admin
from app.db.session import get_db
from app.models.conversation import Conversation
from app.services import analytics_service
from app.utils.exceptions import AppException

from app.schemas.analytics import (
    ConversationSummaryResponse,
    DistributionResponse,
    IssueDistributionResponse,
    OverviewResponse,
    RewriteAdoptionResponse,
    TrendResponse,
    UserSummaryResponse,
)


router = APIRouter()


# ---------------------------------------------------------------------
# Scope convention (see app/services/analytics_service.py docstring):
# an admin sees platform-wide data; a regular user is always scoped to
# their own data. There is no endpoint that lets a regular user see
# another user's aggregate data.
# ---------------------------------------------------------------------
def _scope_user_id(current_user: dict) -> Optional[int]:
    return None if current_user["role"] == "admin" else current_user["id"]


def _to_range(date_from: Optional[date], date_to: Optional[date]):
    start = datetime.combine(date_from, time.min, tzinfo=timezone.utc) if date_from else None
    end = datetime.combine(date_to, time.max, tzinfo=timezone.utc) if date_to else None
    return start, end


@router.get("/overview", response_model=OverviewResponse)
async def overview(
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return {"success": True, "data": analytics_service.get_overview(db)}


@router.get("/civility-trend", response_model=TrendResponse)
async def civility_trend(
    date_from: Optional[date] = Query(default=None),
    date_to: Optional[date] = Query(default=None),
    granularity: str = Query(default="day", pattern="^(day|week|month)$"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    start, end = _to_range(date_from, date_to)
    data = analytics_service.get_civility_trend(
        db,
        date_from=start,
        date_to=end,
        granularity=granularity,
        user_id=_scope_user_id(current_user),
    )
    return {"success": True, "data": data}


@router.get("/civility-distribution", response_model=DistributionResponse)
async def civility_distribution(
    date_from: Optional[date] = Query(default=None),
    date_to: Optional[date] = Query(default=None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    start, end = _to_range(date_from, date_to)
    data = analytics_service.get_civility_distribution(
        db,
        date_from=start,
        date_to=end,
        user_id=_scope_user_id(current_user),
    )
    return {"success": True, "data": data}


@router.get("/users/me/summary", response_model=UserSummaryResponse)
async def my_summary(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    data = analytics_service.get_user_summary(db, user_id=current_user["id"])
    return {"success": True, "data": data}


@router.get("/conversations/{conversation_id}/summary", response_model=ConversationSummaryResponse)
async def conversation_summary(
    conversation_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conversation = db.get(Conversation, conversation_id)

    if conversation is None:
        raise AppException(
            message="Conversation not found.",
            code="CONVERSATION_NOT_FOUND",
            status_code=404,
        )

    if conversation.user_id != current_user["id"] and current_user["role"] != "admin":
        raise AppException(
            message="This conversation does not belong to you.",
            code="CONVERSATION_FORBIDDEN",
            status_code=403,
        )

    data = analytics_service.get_conversation_summary(db, conversation_id=conversation_id)
    return {"success": True, "data": data}


@router.get("/issues/distribution", response_model=IssueDistributionResponse)
async def issues_distribution(
    date_from: Optional[date] = Query(default=None),
    date_to: Optional[date] = Query(default=None),
    limit: int = Query(default=10, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    start, end = _to_range(date_from, date_to)
    data = analytics_service.get_issue_distribution(
        db,
        date_from=start,
        date_to=end,
        user_id=_scope_user_id(current_user),
        limit=limit,
    )
    return {"success": True, "data": data}


@router.get("/rewrites/adoption", response_model=RewriteAdoptionResponse)
async def rewrites_adoption(
    date_from: Optional[date] = Query(default=None),
    date_to: Optional[date] = Query(default=None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    start, end = _to_range(date_from, date_to)
    data = analytics_service.get_rewrite_adoption(
        db,
        date_from=start,
        date_to=end,
        user_id=_scope_user_id(current_user),
    )
    return {"success": True, "data": data}


@router.get("/reports/export")
async def export_report(
    format: str = Query(default="csv"),
    date_from: Optional[date] = Query(default=None),
    date_to: Optional[date] = Query(default=None),
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    if format != "csv":
        raise AppException(
            message="Unsupported export format. Only 'csv' is supported.",
            code="UNSUPPORTED_FORMAT",
            status_code=400,
        )

    start, end = _to_range(date_from, date_to)
    rows = analytics_service.get_daily_report(db, date_from=start, date_to=end)

    buffer = io.StringIO()
    writer = csv.DictWriter(
        buffer,
        fieldnames=[
            "date", "message_count", "avg_civility_score",
            "toxic_count", "toxic_rate",
            "hate_speech_count", "hate_speech_rate",
            "rewrite_count",
        ],
    )
    writer.writeheader()
    writer.writerows(rows)
    buffer.seek(0)

    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=civildialog_report.csv"},
    )
