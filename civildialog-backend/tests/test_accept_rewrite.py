"""
Tests for POST /api/v1/messages/{message_id}/accept-rewrite
(app/db/repositories/moderation_repository.py:accept_rewrite,
app/api/messages.py).

Repository-level tests exercise accept_rewrite() directly against
PostgreSQL via the db_session fixture (SAVEPOINT-rolled-back, see
tests/conftest.py). HTTP-level tests mount only app.api.messages on a
throwaway FastAPI app (same technique as tests/test_analytics.py) to
verify the auth/ownership wiring without importing app.main, which also
pulls in Member 3's NLP pipeline (not installed in this environment).
"""

import pytest
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from app.api.messages import router as messages_router
from app.core.dependencies import get_current_user
from app.db.repositories.moderation_repository import accept_rewrite, save_analysis
from app.db.repositories.message_repository import create_message, get_or_create_conversation
from app.db.session import get_db
from app.models import Message, MessageAnalysis, RewriteSuggestion, User
from app.services import analytics_service
from app.utils.exceptions import AppException


SAMPLE_RESULT = {
    "text": "You are stupid.",
    "preprocessing": {"num_tokens": 3},
    "toxicity": {"is_toxic": True, "toxicity_score": 0.9, "labels": {"toxic": 0.9}},
    "hate_speech": {"is_hate_speech": False, "hate_speech_score": 0.02, "label": "nothate"},
    "sentiment": {"sentiment": "NEGATIVE", "confidence": 0.95},
    "llm_analysis": {
        "is_problematic": True,
        "issues": [],
        "sentiment": "negative",
        "explanation": "Personal attack.",
        "rewrite": "I disagree with your point.",
        "suggestions": ["Focus on the argument."],
        "confidence": 0.9,
    },
    "civility_score": 30,
}


def _user(db, email="accept-rewrite-test@example.invalid"):
    user = User(name="Accept Test", email=email, password_hash="x")
    db.add(user)
    db.flush()
    return user


def _message_with_rewrite(db, user, *, problematic=True):
    conversation = get_or_create_conversation(db, user_id=user.id, conversation_id=None)
    message = create_message(
        db, conversation_id=conversation.id, user_id=user.id, original_text=SAMPLE_RESULT["text"]
    )
    result = dict(SAMPLE_RESULT)
    if not problematic:
        result["llm_analysis"] = {**result["llm_analysis"], "is_problematic": False, "rewrite": ""}
    save_analysis(db, message=message, civility_score=result["civility_score"], moderation_result=result)
    db.flush()
    return message


class TestAcceptRewriteRepository:
    def test_successful_acceptance_updates_rewrite_and_message(self, db_session):
        user = _user(db_session)
        message = _message_with_rewrite(db_session, user)

        rewrite = accept_rewrite(db_session, message_id=message.id, user_id=user.id, is_admin=False)

        assert rewrite.was_accepted is True
        assert rewrite.accepted_at is not None

        db_session.flush()
        db_session.refresh(message)
        # final_text update
        assert message.final_text == "I disagree with your point."
        # was_rewritten update
        assert message.was_rewritten is True

    def test_unauthorized_user_cannot_accept(self, db_session):
        owner = _user(db_session, email="owner-ar@example.invalid")
        other = _user(db_session, email="other-ar@example.invalid")
        message = _message_with_rewrite(db_session, owner)

        with pytest.raises(AppException) as exc_info:
            accept_rewrite(db_session, message_id=message.id, user_id=other.id, is_admin=False)

        assert exc_info.value.status_code == 403
        assert exc_info.value.code == "MESSAGE_FORBIDDEN"

    def test_admin_can_accept_another_users_message(self, db_session):
        owner = _user(db_session, email="owner-ar2@example.invalid")
        admin = _user(db_session, email="admin-ar2@example.invalid", )
        message = _message_with_rewrite(db_session, owner)

        rewrite = accept_rewrite(db_session, message_id=message.id, user_id=admin.id, is_admin=True)
        assert rewrite.was_accepted is True

    def test_nonexistent_message_raises_404(self, db_session):
        user = _user(db_session)

        with pytest.raises(AppException) as exc_info:
            accept_rewrite(db_session, message_id=999_999_999, user_id=user.id, is_admin=False)

        assert exc_info.value.status_code == 404
        assert exc_info.value.code == "MESSAGE_NOT_FOUND"

    def test_message_with_no_analysis_raises_404(self, db_session):
        user = _user(db_session)
        conversation = get_or_create_conversation(db_session, user_id=user.id, conversation_id=None)
        message = create_message(
            db_session, conversation_id=conversation.id, user_id=user.id, original_text="unanalyzed"
        )
        db_session.flush()

        with pytest.raises(AppException) as exc_info:
            accept_rewrite(db_session, message_id=message.id, user_id=user.id, is_admin=False)

        assert exc_info.value.status_code == 404
        assert exc_info.value.code == "ANALYSIS_NOT_FOUND"

    def test_no_rewrite_suggestion_raises_404(self, db_session):
        user = _user(db_session)
        # not problematic -> save_analysis deliberately creates no RewriteSuggestion row
        message = _message_with_rewrite(db_session, user, problematic=False)

        with pytest.raises(AppException) as exc_info:
            accept_rewrite(db_session, message_id=message.id, user_id=user.id, is_admin=False)

        assert exc_info.value.status_code == 404
        assert exc_info.value.code == "REWRITE_SUGGESTION_NOT_FOUND"

    def test_already_accepted_rewrite_raises_409(self, db_session):
        user = _user(db_session)
        message = _message_with_rewrite(db_session, user)

        accept_rewrite(db_session, message_id=message.id, user_id=user.id, is_admin=False)

        with pytest.raises(AppException) as exc_info:
            accept_rewrite(db_session, message_id=message.id, user_id=user.id, is_admin=False)

        assert exc_info.value.status_code == 409
        assert exc_info.value.code == "REWRITE_ALREADY_ACCEPTED"

    def test_rewrite_adoption_analytics_reflects_acceptance(self, db_session):
        user = _user(db_session)
        message = _message_with_rewrite(db_session, user)

        before = analytics_service.get_rewrite_adoption(db_session, user_id=user.id)
        assert before["total_suggestions"] == 1
        assert before["accepted"] == 0

        accept_rewrite(db_session, message_id=message.id, user_id=user.id, is_admin=False)
        db_session.flush()

        after = analytics_service.get_rewrite_adoption(db_session, user_id=user.id)
        assert after["total_suggestions"] == 1
        assert after["accepted"] == 1
        assert after["adoption_percentage"] == 100.0


@pytest.fixture
def client(db_session):
    app = FastAPI()

    @app.exception_handler(AppException)
    async def _app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"success": False, "error": {"code": exc.code, "message": exc.message}},
        )

    app.include_router(messages_router, prefix="/api/v1/messages")
    app.dependency_overrides[get_db] = lambda: db_session

    def _as(user):
        return lambda: {"id": user.id, "name": user.name, "email": user.email, "role": "user"}

    def _as_admin(user):
        return lambda: {"id": user.id, "name": user.name, "email": user.email, "role": "admin"}

    test_client = TestClient(app)
    test_client.app_ref = app
    test_client.login_as = lambda user: app.dependency_overrides.update({get_current_user: _as(user)})
    test_client.login_as_admin = lambda user: app.dependency_overrides.update({get_current_user: _as_admin(user)})

    yield test_client


class TestAcceptRewriteHTTP:
    def test_owner_accepts_via_http_200(self, client, db_session):
        user = _user(db_session, email="http-owner@example.invalid")
        message = _message_with_rewrite(db_session, user)

        client.login_as(user)
        resp = client.post(f"/api/v1/messages/{message.id}/accept-rewrite")

        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert body["data"]["was_accepted"] is True
        assert body["data"]["was_rewritten"] is True
        assert body["data"]["final_text"] == "I disagree with your point."

    def test_non_owner_gets_403_via_http(self, client, db_session):
        owner = _user(db_session, email="http-owner2@example.invalid")
        other = _user(db_session, email="http-other2@example.invalid")
        message = _message_with_rewrite(db_session, owner)

        client.login_as(other)
        resp = client.post(f"/api/v1/messages/{message.id}/accept-rewrite")

        assert resp.status_code == 403
        assert resp.json()["error"]["code"] == "MESSAGE_FORBIDDEN"

    def test_nonexistent_message_404_via_http(self, client, db_session):
        user = _user(db_session, email="http-none@example.invalid")
        client.login_as(user)

        resp = client.post("/api/v1/messages/999999999/accept-rewrite")

        assert resp.status_code == 404
        assert resp.json()["error"]["code"] == "MESSAGE_NOT_FOUND"

    def test_admin_can_accept_others_message_via_http(self, client, db_session):
        owner = _user(db_session, email="http-owner3@example.invalid")
        admin = _user(db_session, email="http-admin3@example.invalid")
        message = _message_with_rewrite(db_session, owner)

        client.login_as_admin(admin)
        resp = client.post(f"/api/v1/messages/{message.id}/accept-rewrite")

        assert resp.status_code == 200
        assert resp.json()["data"]["was_accepted"] is True

    def test_double_accept_returns_409_via_http(self, client, db_session):
        user = _user(db_session, email="http-dup@example.invalid")
        message = _message_with_rewrite(db_session, user)

        client.login_as(user)
        first = client.post(f"/api/v1/messages/{message.id}/accept-rewrite")
        assert first.status_code == 200

        second = client.post(f"/api/v1/messages/{message.id}/accept-rewrite")
        assert second.status_code == 409
        assert second.json()["error"]["code"] == "REWRITE_ALREADY_ACCEPTED"
