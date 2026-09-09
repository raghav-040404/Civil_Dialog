"""
Tests for the Phase C persistence layer:
  app/db/repositories/message_repository.py
  app/db/repositories/moderation_repository.py
  app/db/repositories/user_repository.py

These do not call app.services.moderation_service.analyze_and_persist()
directly, because importing that module transitively imports Member 3's
NLP pipeline (spacy/transformers/torch) and Member 4's LLM client, none
of which are installed in this lightweight test environment. Instead,
each repository function -- which is exactly the code this task added --
is exercised directly against PostgreSQL with a synthetic
ModerationResult-shaped dict, matching what analyze_text() actually
returns (see app/schemas/moderation.py:ModerationResult).
"""

import pytest
from sqlalchemy.exc import IntegrityError

from app.models import (
    AnalysisIssue,
    Conversation,
    Message,
    MessageAnalysis,
    RewriteSuggestion,
    User,
)
from app.db.repositories.message_repository import (
    create_message,
    get_or_create_conversation,
    refresh_conversation_stats,
)
from app.db.repositories.moderation_repository import save_analysis
from app.db.repositories import user_repository
from app.utils.exceptions import AppException


SAMPLE_MODERATION_RESULT = {
    "text": "You are stupid. Nobody agrees with you.",
    "preprocessing": {
        "original_text": "You are stupid. Nobody agrees with you.",
        "tokens": [{"text": "You", "lemma": "you", "pos": "PRON", "is_stop": True, "is_punct": False}],
        "num_tokens": 8,
    },
    "toxicity": {
        "is_toxic": True,
        "toxicity_score": 0.91,
        "labels": {"toxic": 0.91, "insult": 0.85, "obscene": 0.2, "threat": 0.01, "severe_toxic": 0.1, "identity_hate": 0.02},
    },
    "hate_speech": {
        "is_hate_speech": False,
        "hate_speech_score": 0.05,
        "label": "nothate",
    },
    "sentiment": {
        "sentiment": "NEGATIVE",
        "confidence": 0.97,
    },
    "timestamp": "2026-09-08T00:00:00+00:00",
    "fallacies": ["ad_hominem"],
    "feedback": "This message contains a personal attack.",
    "rewrite": "I disagree with your reasoning here.",
    "llm_analysis": {
        "is_problematic": True,
        "issues": [
            {"type": "ad_hominem", "severity": "high", "confidence": 0.89, "evidence": "You are stupid"},
        ],
        "sentiment": "negative",
        "explanation": "This message contains a personal attack.",
        "rewrite": "I disagree with your reasoning here.",
        "suggestions": ["Focus on the argument, not the person."],
        "confidence": 0.9,
    },
    "civility_score": 30,
}


def _make_user(db, email="persist-test@example.invalid"):
    user = User(name="Persist Test", email=email, password_hash="x")
    db.add(user)
    db.flush()
    return user


class TestConversationResolution:
    def test_omitting_conversation_id_creates_a_new_conversation(self, db_session):
        user = _make_user(db_session)

        conversation = get_or_create_conversation(
            db_session, user_id=user.id, conversation_id=None
        )

        assert conversation.id is not None
        assert conversation.user_id == user.id

    def test_passing_conversation_id_reuses_it(self, db_session):
        user = _make_user(db_session)
        existing = Conversation(user_id=user.id)
        db_session.add(existing)
        db_session.flush()

        resolved = get_or_create_conversation(
            db_session, user_id=user.id, conversation_id=existing.id
        )

        assert resolved.id == existing.id

    def test_nonexistent_conversation_id_raises_404(self, db_session):
        user = _make_user(db_session)

        with pytest.raises(AppException) as exc_info:
            get_or_create_conversation(db_session, user_id=user.id, conversation_id=999_999_999)

        assert exc_info.value.status_code == 404

    def test_conversation_owned_by_another_user_raises_403(self, db_session):
        owner = _make_user(db_session, email="owner@example.invalid")
        other = _make_user(db_session, email="other@example.invalid")

        conversation = Conversation(user_id=owner.id)
        db_session.add(conversation)
        db_session.flush()

        with pytest.raises(AppException) as exc_info:
            get_or_create_conversation(db_session, user_id=other.id, conversation_id=conversation.id)

        assert exc_info.value.status_code == 403


class TestSaveAnalysis:
    def test_full_flow_creates_message_analysis_issue_and_rewrite(self, db_session):
        user = _make_user(db_session)
        conversation = get_or_create_conversation(db_session, user_id=user.id, conversation_id=None)

        message = create_message(
            db_session,
            conversation_id=conversation.id,
            user_id=user.id,
            original_text=SAMPLE_MODERATION_RESULT["text"],
        )

        analysis = save_analysis(
            db_session,
            message=message,
            civility_score=SAMPLE_MODERATION_RESULT["civility_score"],
            moderation_result=SAMPLE_MODERATION_RESULT,
        )

        db_session.flush()

        assert analysis.message_id == message.id
        assert message.conversation_id == conversation.id
        assert message.user_id == user.id
        assert float(analysis.civility_score) == 30.0
        assert analysis.score_version == "1.0.0"
        assert analysis.is_toxic is True
        assert analysis.num_tokens == 8
        assert analysis.raw_data == {"toxicity_labels": SAMPLE_MODERATION_RESULT["toxicity"]["labels"]}

        issues = db_session.query(AnalysisIssue).filter_by(analysis_id=analysis.id).all()
        assert len(issues) == 1
        assert issues[0].issue_type == "ad_hominem"
        assert issues[0].severity == "high"

        rewrites = db_session.query(RewriteSuggestion).filter_by(analysis_id=analysis.id).all()
        assert len(rewrites) == 1
        assert rewrites[0].rewrite_text == "I disagree with your reasoning here."
        assert rewrites[0].suggestions == ["Focus on the argument, not the person."]

    def test_no_rewrite_row_when_not_problematic(self, db_session):
        user = _make_user(db_session)
        conversation = get_or_create_conversation(db_session, user_id=user.id, conversation_id=None)
        message = create_message(
            db_session, conversation_id=conversation.id, user_id=user.id, original_text="Great point, thank you."
        )

        clean_result = dict(SAMPLE_MODERATION_RESULT)
        clean_result["llm_analysis"] = {
            "is_problematic": False, "issues": [], "sentiment": "positive",
            "explanation": "Constructive.", "rewrite": "Great point, thank you.",
            "suggestions": [], "confidence": 1.0,
        }

        analysis = save_analysis(
            db_session, message=message, civility_score=100, moderation_result=clean_result
        )
        db_session.flush()

        assert db_session.query(RewriteSuggestion).filter_by(analysis_id=analysis.id).count() == 0
        assert db_session.query(AnalysisIssue).filter_by(analysis_id=analysis.id).count() == 0

    def test_num_tokens_stored_but_not_token_array(self, db_session):
        user = _make_user(db_session)
        conversation = get_or_create_conversation(db_session, user_id=user.id, conversation_id=None)
        message = create_message(
            db_session, conversation_id=conversation.id, user_id=user.id, original_text="hi"
        )
        analysis = save_analysis(
            db_session, message=message, civility_score=30, moderation_result=SAMPLE_MODERATION_RESULT
        )
        db_session.flush()

        assert analysis.num_tokens == 8
        assert "tokens" not in (analysis.raw_data or {})
        assert "preprocessing" not in (analysis.raw_data or {})


class TestConversationStats:
    def test_refresh_conversation_stats_computes_correct_aggregate(self, db_session):
        user = _make_user(db_session)
        conversation = get_or_create_conversation(db_session, user_id=user.id, conversation_id=None)

        for score in (100, 50, 0):
            message = create_message(
                db_session, conversation_id=conversation.id, user_id=user.id, original_text=f"msg {score}"
            )
            save_analysis(
                db_session, message=message, civility_score=score,
                moderation_result={**SAMPLE_MODERATION_RESULT, "civility_score": score},
            )

        refresh_conversation_stats(db_session, conversation)
        db_session.flush()

        assert conversation.message_count == 3
        assert float(conversation.avg_civility_score) == 50.0


class TestTransactionRollback:
    def test_rollback_discards_message_and_analysis(self, db_session):
        user = _make_user(db_session)
        conversation = get_or_create_conversation(db_session, user_id=user.id, conversation_id=None)
        message = create_message(
            db_session, conversation_id=conversation.id, user_id=user.id, original_text="will be rolled back"
        )
        analysis = save_analysis(
            db_session, message=message, civility_score=30, moderation_result=SAMPLE_MODERATION_RESULT
        )
        db_session.flush()

        message_id, analysis_id, conversation_id = message.id, analysis.id, conversation.id

        # Simulate what app/db/session.py:get_db() does when a request fails
        # partway through: roll back everything written in this transaction.
        db_session.rollback()

        assert db_session.get(Message, message_id) is None
        assert db_session.get(MessageAnalysis, analysis_id) is None
        assert db_session.get(Conversation, conversation_id) is None

    def test_invalid_message_fk_leaves_no_partial_analysis(self, db_session):
        user = _make_user(db_session)

        bad_message = Message(conversation_id=999_999_999, user_id=user.id, original_text="orphan")
        db_session.add(bad_message)

        with pytest.raises(IntegrityError):
            db_session.flush()

        db_session.rollback()

        assert db_session.query(Message).filter_by(original_text="orphan").count() == 0


class TestUserRepository:
    """
    user_repository.py manages its own short-lived sessions (see its
    module docstring) rather than accepting a db_session parameter, so it
    is not covered by the SAVEPOINT rollback used above. Rows created
    here are deleted explicitly in a finally block so the development
    database is left clean regardless of test outcome.
    """

    def test_create_then_find_by_email_and_id(self):
        created = user_repository.create_user(
            name="Repo Test", email="repo-test@example.invalid", password_hash="hashed"
        )
        try:
            assert created["role"] == "user"

            by_email = user_repository.find_user_by_email("repo-test@example.invalid")
            assert by_email is not None
            assert by_email["id"] == created["id"]

            by_id = user_repository.find_user_by_id(created["id"])
            assert by_id is not None
            assert by_id["email"] == "repo-test@example.invalid"
        finally:
            from app.db.database import SessionLocal
            with SessionLocal() as cleanup_db:
                cleanup_db.query(User).filter_by(id=created["id"]).delete()
                cleanup_db.commit()

    def test_find_by_email_is_case_insensitive(self):
        created = user_repository.create_user(
            name="Case Test", email="CaseTest@Example.invalid", password_hash="hashed"
        )
        try:
            assert created["email"] == "casetest@example.invalid"
            found = user_repository.find_user_by_email("CASETEST@EXAMPLE.INVALID")
            assert found is not None
            assert found["id"] == created["id"]
        finally:
            from app.db.database import SessionLocal
            with SessionLocal() as cleanup_db:
                cleanup_db.query(User).filter_by(id=created["id"]).delete()
                cleanup_db.commit()

    def test_find_nonexistent_user_returns_none(self):
        assert user_repository.find_user_by_email("does-not-exist@example.invalid") is None
        assert user_repository.find_user_by_id(999_999_999) is None
