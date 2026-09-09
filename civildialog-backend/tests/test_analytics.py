"""
End-to-end tests for the analytics + history HTTP endpoints
(app/api/analytics.py, app/api/history.py, app/services/analytics_service.py).

These mount the REAL router modules on a throwaway FastAPI app (not
app.main, which also imports app.api.moderation -> Member 3's NLP
pipeline -> spacy/transformers/torch, none of which are installed in
this lightweight test environment -- unrelated to the code under test
here). Only the auth dependencies (get_current_user / require_admin) and
get_db are overridden, which is standard FastAPI testing practice, not a
shortcut around the analytics logic itself: every request below exercises
the real endpoint function, the real Pydantic response model, the real
app.services.analytics_service SQL, against the real (test-transaction
scoped) PostgreSQL database.
"""

from datetime import datetime, timezone

import pytest
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from app.api.analytics import router as analytics_router
from app.api.history import router as history_router
from app.core.dependencies import get_current_user, require_admin
from app.db.session import get_db
from app.models import (
    AnalysisIssue,
    Conversation,
    Message,
    MessageAnalysis,
    RewriteSuggestion,
    User,
)
from app.utils.exceptions import AppException

# Fixed far-future timestamp for every row this test file creates. Real
# usage (including scripts/seed_data.py, which spreads rows across the
# last 30 days) can never land here, so any query bounded to this window
# is isolated from whatever else happens to be in the database --
# necessary because these tests run against the same PostgreSQL instance
# a developer may have already run scripts/seed_data.py against.
FIXTURE_TIME = datetime(2030, 6, 15, tzinfo=timezone.utc)
FIXTURE_WINDOW = {"date_from": "2030-06-01", "date_to": "2030-06-30"}


def _seed(db):
    """Two users, a few conversations/messages/analyses/issues/rewrites."""
    alice = User(name="Alice", email="alice-an@example.invalid", password_hash="x")
    bob = User(name="Bob", email="bob-an@example.invalid", password_hash="x")
    db.add_all([alice, bob])
    db.flush()

    conv_a = Conversation(user_id=alice.id)
    conv_b = Conversation(user_id=bob.id)
    db.add_all([conv_a, conv_b])
    db.flush()

    def _msg(conv, user, text, score, toxic, hate, sentiment):
        m = Message(conversation_id=conv.id, user_id=user.id, original_text=text)
        db.add(m)
        db.flush()
        a = MessageAnalysis(
            message_id=m.id, civility_score=score,
            toxicity_score=0.9 if toxic else 0.1, is_toxic=toxic,
            hate_speech_score=0.9 if hate else 0.0, is_hate_speech=hate,
            sentiment=sentiment,
            analyzed_at=FIXTURE_TIME,
        )
        db.add(a)
        db.flush()
        return m, a

    m1, a1 = _msg(conv_a, alice, "you are an idiot", 20, True, False, "NEGATIVE")
    db.add(AnalysisIssue(analysis_id=a1.id, issue_type="ad_hominem", severity="high", confidence=0.9))
    db.add(RewriteSuggestion(analysis_id=a1.id, rewrite_text="I disagree.", was_accepted=True, created_at=FIXTURE_TIME))

    m2, a2 = _msg(conv_a, alice, "great point!", 100, False, False, "POSITIVE")

    m3, a3 = _msg(conv_b, bob, "you people are all the same", 10, False, True, "NEGATIVE")
    db.add(AnalysisIssue(analysis_id=a3.id, issue_type="hasty_generalization", severity="medium", confidence=0.7))
    db.add(RewriteSuggestion(analysis_id=a3.id, rewrite_text="Let's discuss the policy itself.", was_accepted=False, created_at=FIXTURE_TIME))

    db.flush()
    return {"alice": alice, "bob": bob, "conv_a": conv_a, "conv_b": conv_b}


@pytest.fixture
def client(db_session):
    app = FastAPI()

    # Mirrors app/main.py's AppException handler -- without it, AppException
    # (raised by require_admin / ownership checks / format validation) would
    # propagate as an unhandled exception instead of the real 4xx JSON
    # response the production app returns.
    @app.exception_handler(AppException)
    async def _app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"success": False, "error": {"code": exc.code, "message": exc.message}},
        )

    app.include_router(analytics_router, prefix="/api/v1/analytics")
    app.include_router(history_router, prefix="/api/v1/history")

    app.dependency_overrides[get_db] = lambda: db_session

    # /overview has no date filter (it reports true all-time totals), so it
    # cannot be isolated from pre-existing data (e.g. scripts/seed_data.py)
    # the way the other endpoints are below. Capture a baseline immediately
    # before seeding so overview tests can assert on the delta instead.
    from app.services.analytics_service import get_overview
    overview_baseline = get_overview(db_session)

    seeded = _seed(db_session)

    def _as(user):
        return lambda: {"id": user.id, "name": user.name, "email": user.email, "role": "user"}

    def _as_admin():
        return {"id": 999, "name": "Admin", "email": "admin@example.invalid", "role": "admin"}

    test_client = TestClient(app)
    test_client.seeded = seeded
    test_client.app_ref = app
    test_client.overview_baseline = overview_baseline
    test_client.as_alice = lambda: app.dependency_overrides.update({get_current_user: _as(seeded["alice"])})
    test_client.as_bob = lambda: app.dependency_overrides.update({get_current_user: _as(seeded["bob"])})
    test_client.as_admin = lambda: app.dependency_overrides.update({
        get_current_user: _as_admin, require_admin: _as_admin
    })

    yield test_client


class TestOverview:
    def test_overview_requires_admin(self, client):
        client.as_alice()
        # require_admin is NOT overridden -- only get_current_user is. Since
        # FastAPI substitutes overridden dependencies everywhere they appear
        # in the tree (including inside require_admin's own
        # Depends(get_current_user)), the real require_admin logic runs
        # against alice's role="user" and must reject her.
        resp = client.get("/api/v1/analytics/overview")
        assert resp.status_code == 403

    def test_overview_totals_for_admin(self, client):
        # /overview reports true all-time totals with no date filter, so it
        # cannot be isolated from whatever else is already in the database
        # (e.g. scripts/seed_data.py output) -- assert on the delta this
        # fixture's own rows caused, not on absolute counts.
        before = client.overview_baseline
        client.as_admin()
        resp = client.get("/api/v1/analytics/overview")
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["total_users"] - before["total_users"] == 2
        assert data["total_messages"] - before["total_messages"] == 3
        assert data["toxic_message_count"] - before["toxic_message_count"] == 1
        assert data["hate_speech_count"] - before["hate_speech_count"] == 1
        assert data["rewrite_offered_count"] - before["rewrite_offered_count"] == 2
        assert data["rewrite_accepted_count"] - before["rewrite_accepted_count"] == 1


class TestDistributionAndTrend:
    def test_civility_distribution_buckets(self, client):
        client.as_admin()
        resp = client.get("/api/v1/analytics/civility-distribution", params=FIXTURE_WINDOW)
        assert resp.status_code == 200
        buckets = {b["range"]: b["count"] for b in resp.json()["data"]}
        assert buckets["0-20"] == 2   # scores 20 and 10
        assert buckets["81-100"] == 1  # score 100

    def test_civility_trend_returns_points(self, client):
        client.as_admin()
        resp = client.get("/api/v1/analytics/civility-trend", params=FIXTURE_WINDOW)
        assert resp.status_code == 200
        points = resp.json()["data"]
        assert len(points) == 1  # all seeded analyses share one date
        assert points[0]["message_count"] == 3


class TestUserScoping:
    def test_regular_user_sees_only_their_own_trend(self, client):
        client.as_alice()
        resp = client.get("/api/v1/analytics/civility-trend")
        assert resp.status_code == 200
        assert resp.json()["data"][0]["message_count"] == 2  # alice has 2 messages, not 3

    def test_users_me_summary(self, client):
        client.as_alice()
        resp = client.get("/api/v1/analytics/users/me/summary")
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["message_count"] == 2
        assert data["toxic_count"] == 1
        assert data["rewrite_count"] == 1
        assert data["accepted_rewrite_count"] == 1


class TestConversationSummaryAuthorization:
    def test_owner_can_view_summary(self, client):
        client.as_alice()
        conv_id = client.seeded["conv_a"].id
        resp = client.get(f"/api/v1/analytics/conversations/{conv_id}/summary")
        assert resp.status_code == 200
        assert resp.json()["data"]["message_count"] == 2

    def test_non_owner_forbidden(self, client):
        client.as_bob()
        conv_id = client.seeded["conv_a"].id
        resp = client.get(f"/api/v1/analytics/conversations/{conv_id}/summary")
        assert resp.status_code == 403

    def test_nonexistent_conversation_404(self, client):
        client.as_alice()
        resp = client.get("/api/v1/analytics/conversations/999999999/summary")
        assert resp.status_code == 404


class TestIssuesAndRewrites:
    def test_issue_distribution(self, client):
        client.as_admin()
        resp = client.get("/api/v1/analytics/issues/distribution", params=FIXTURE_WINDOW)
        assert resp.status_code == 200
        types = {i["issue_type"] for i in resp.json()["data"]}
        assert types == {"ad_hominem", "hasty_generalization"}

    def test_rewrite_adoption(self, client):
        client.as_admin()
        resp = client.get("/api/v1/analytics/rewrites/adoption", params=FIXTURE_WINDOW)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["total_suggestions"] == 2
        assert data["accepted"] == 1
        assert data["rejected"] == 1
        assert data["adoption_percentage"] == 50.0


class TestHistory:
    def test_history_is_scoped_and_paginated_newest_first(self, client):
        client.as_alice()
        resp = client.get("/api/v1/history/messages?limit=1&offset=0")
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["total"] == 2  # alice's own messages only, not bob's
        assert len(data["items"]) == 1
        assert data["items"][0]["original_text"] == "great point!"  # created after m1

    def test_history_cannot_see_another_users_messages(self, client):
        client.as_bob()
        resp = client.get("/api/v1/history/messages")
        data = resp.json()["data"]
        texts = [i["original_text"] for i in data["items"]]
        assert "you are an idiot" not in texts
        assert "great point!" not in texts


class TestReportExport:
    def test_csv_export_requires_admin(self, client):
        client.as_alice()
        resp = client.get("/api/v1/analytics/reports/export?format=csv")
        assert resp.status_code == 403

    def test_csv_export_returns_csv(self, client):
        client.as_admin()
        resp = client.get("/api/v1/analytics/reports/export?format=csv")
        assert resp.status_code == 200
        assert resp.headers["content-type"].startswith("text/csv")
        assert "date,message_count,avg_civility_score" in resp.text

    def test_unsupported_format_rejected(self, client):
        client.as_admin()
        resp = client.get("/api/v1/analytics/reports/export?format=pdf")
        assert resp.status_code == 400
