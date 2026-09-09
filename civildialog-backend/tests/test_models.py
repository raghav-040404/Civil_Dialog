"""
Database layer tests for the ORM models (Phase B).

Requires PostgreSQL running (docker compose up -d) and migrations applied
(alembic upgrade head). Every test runs inside tests/conftest.py's
db_session fixture, which rolls back afterwards — nothing here is ever
committed to the real database.
"""

import pytest
from sqlalchemy.exc import IntegrityError

from app.models import (
    User,
    Conversation,
    Message,
    MessageAnalysis,
    AnalysisIssue,
    RewriteSuggestion,
)


def _make_user(db, email="model-test@example.invalid"):
    user = User(name="Model Test", email=email, password_hash="x")
    db.add(user)
    db.flush()
    return user


def _make_message(db, user):
    conversation = Conversation(user_id=user.id)
    db.add(conversation)
    db.flush()

    message = Message(
        conversation_id=conversation.id,
        user_id=user.id,
        original_text="hello world",
    )
    db.add(message)
    db.flush()
    return conversation, message


def test_user_creation_applies_defaults(db_session):
    user = _make_user(db_session)

    assert user.id is not None
    assert user.role == "user"
    assert user.is_active is True


def test_conversation_creation_and_fk_to_user(db_session):
    user = _make_user(db_session)
    conversation = Conversation(user_id=user.id)
    db_session.add(conversation)
    db_session.flush()

    assert conversation.id is not None
    assert conversation.status == "active"
    assert conversation.message_count == 0
    assert conversation.user_id == user.id


def test_message_creation_and_fks(db_session):
    user = _make_user(db_session)
    conversation, message = _make_message(db_session, user)

    assert message.id is not None
    assert message.conversation_id == conversation.id
    assert message.user_id == user.id
    assert message.was_rewritten is False


def test_message_analysis_creation(db_session):
    user = _make_user(db_session)
    _, message = _make_message(db_session, user)

    analysis = MessageAnalysis(
        message_id=message.id,
        civility_score=88.5,
        toxicity_score=0.05,
        is_toxic=False,
        hate_speech_score=0.01,
        is_hate_speech=False,
    )
    db_session.add(analysis)
    db_session.flush()

    assert analysis.id is not None
    assert analysis.score_version == "1.0.0"


def test_analysis_issue_creation(db_session):
    user = _make_user(db_session)
    _, message = _make_message(db_session, user)
    analysis = MessageAnalysis(
        message_id=message.id, civility_score=40.0,
        toxicity_score=0.6, is_toxic=True,
        hate_speech_score=0.0, is_hate_speech=False,
    )
    db_session.add(analysis)
    db_session.flush()

    issue = AnalysisIssue(
        analysis_id=analysis.id,
        issue_type="ad_hominem",
        severity="medium",
        confidence=0.75,
        evidence="you're an idiot",
    )
    db_session.add(issue)
    db_session.flush()

    assert issue.id is not None
    assert issue.analysis_id == analysis.id


def test_rewrite_suggestion_creation(db_session):
    user = _make_user(db_session)
    _, message = _make_message(db_session, user)
    analysis = MessageAnalysis(
        message_id=message.id, civility_score=40.0,
        toxicity_score=0.6, is_toxic=True,
        hate_speech_score=0.0, is_hate_speech=False,
    )
    db_session.add(analysis)
    db_session.flush()

    rewrite = RewriteSuggestion(
        analysis_id=analysis.id,
        rewrite_text="I disagree with your point.",
        suggestions=["stay on topic", "avoid insults"],
    )
    db_session.add(rewrite)
    db_session.flush()

    assert rewrite.id is not None
    assert rewrite.was_accepted is None
    assert rewrite.created_at is not None


def test_message_requires_valid_conversation_fk(db_session):
    user = _make_user(db_session)

    bad_message = Message(
        conversation_id=999_999_999,  # does not exist
        user_id=user.id,
        original_text="orphan message",
    )
    db_session.add(bad_message)

    with pytest.raises(IntegrityError):
        db_session.flush()


def test_message_analysis_message_id_is_unique(db_session):
    user = _make_user(db_session)
    _, message = _make_message(db_session, user)

    db_session.add(MessageAnalysis(
        message_id=message.id, civility_score=90.0,
        toxicity_score=0.0, is_toxic=False,
        hate_speech_score=0.0, is_hate_speech=False,
    ))
    db_session.flush()

    # a second analysis for the SAME message must violate the unique
    # constraint on message_analyses.message_id (one analysis per message)
    db_session.add(MessageAnalysis(
        message_id=message.id, civility_score=10.0,
        toxicity_score=0.9, is_toxic=True,
        hate_speech_score=0.0, is_hate_speech=False,
    ))

    with pytest.raises(IntegrityError):
        db_session.flush()


def test_deleting_analysis_cascades_to_issues_and_rewrites(db_session):
    user = _make_user(db_session)
    _, message = _make_message(db_session, user)
    analysis = MessageAnalysis(
        message_id=message.id, civility_score=20.0,
        toxicity_score=0.8, is_toxic=True,
        hate_speech_score=0.0, is_hate_speech=False,
    )
    db_session.add(analysis)
    db_session.flush()

    db_session.add(AnalysisIssue(analysis_id=analysis.id, issue_type="strawman"))
    db_session.add(RewriteSuggestion(analysis_id=analysis.id, rewrite_text="be nicer"))
    db_session.flush()

    db_session.delete(analysis)
    db_session.flush()

    remaining_issues = db_session.query(AnalysisIssue).filter_by(analysis_id=analysis.id).count()
    remaining_rewrites = db_session.query(RewriteSuggestion).filter_by(analysis_id=analysis.id).count()

    assert remaining_issues == 0
    assert remaining_rewrites == 0
