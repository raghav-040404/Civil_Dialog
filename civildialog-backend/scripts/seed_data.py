"""
Development seed data for CivilDialog.

Populates enough realistic data to exercise every analytics endpoint:
several users (incl. one admin), multiple conversations, messages
spanning a range of Civility Scores / toxicity / hate-speech / sentiment,
analysis issues, and rewrite suggestions in accepted / rejected / pending
states.

Usage (from civildialog-backend/, with PostgreSQL running and migrations
applied):

    .venv/Scripts/python scripts/seed_data.py

Safe to re-run: existing rows for the fixed seed emails below are deleted
(cascading to their conversations/messages/analyses/issues/rewrites) before
new ones are inserted, so running this twice does not create duplicates
or violate the unique email constraint.

The password below ("SeedPassword123!") is a fixed, publicly-known
development-only credential for these seed accounts -- it is not a
secret and must never be reused for a real account.
"""

import os
import random
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.security import hash_password
from app.db.database import SessionLocal
from app.models import (
    AnalysisIssue,
    Conversation,
    Message,
    MessageAnalysis,
    RewriteSuggestion,
    User,
)

SEED_PASSWORD_HASH = hash_password("SeedPassword123!")

SEED_USERS = [
    {"name": "Alice Admin", "email": "alice.admin@civildialog.seed", "role": "admin"},
    {"name": "Bilal Khan", "email": "bilal@civildialog.seed", "role": "user"},
    {"name": "Chidi Okafor", "email": "chidi@civildialog.seed", "role": "user"},
    {"name": "Diya Sharma", "email": "diya@civildialog.seed", "role": "user"},
    {"name": "Elena Petrova", "email": "elena@civildialog.seed", "role": "user"},
    {"name": "Farid Haidari", "email": "farid@civildialog.seed", "role": "user"},
]

SAMPLE_MESSAGES = [
    # (text, civility_score, is_toxic, is_hate_speech, sentiment, issue_type, was_rewritten)
    ("I think we should reconsider the budget allocation for next quarter.", 98, False, False, "POSITIVE", None, False),
    ("That's a fair point, thanks for explaining your reasoning.", 96, False, False, "POSITIVE", None, False),
    ("I disagree, but I see where you're coming from.", 88, False, False, "NEUTRAL", None, False),
    ("This proposal has some issues we should discuss calmly.", 82, False, False, "NEUTRAL", None, False),
    ("Honestly this whole plan seems poorly thought out.", 61, False, False, "NEGATIVE", "hasty_generalization", False),
    ("You clearly didn't do any research before saying that.", 45, True, False, "NEGATIVE", "ad_hominem", True),
    ("Only an idiot would support this policy.", 28, True, False, "NEGATIVE", "ad_hominem", True),
    ("People like you always ruin these discussions.", 15, True, True, "NEGATIVE", "personal_attack", True),
    ("Shut up, nobody asked for your opinion.", 20, True, False, "NEGATIVE", "ad_hominem", True),
    ("Your entire group is the reason this city has problems.", 8, True, True, "NEGATIVE", "hate_speech", True),
]

REWRITE_TEXT = {
    "ad_hominem": "I disagree with your position and would like to understand your reasoning better.",
    "personal_attack": "I think we have different perspectives here -- let's focus on the issue.",
    "hate_speech": "I have concerns about this policy's impact on the community.",
}


def _random_timestamp(days_back: int) -> datetime:
    return datetime.now(timezone.utc) - timedelta(
        days=random.randint(0, days_back),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
    )


def seed() -> None:
    db = SessionLocal()

    try:
        seed_emails = [u["email"] for u in SEED_USERS]
        existing_ids = [
            row[0] for row in db.query(User.id).filter(User.email.in_(seed_emails)).all()
        ]
        if existing_ids:
            db.query(User).filter(User.id.in_(existing_ids)).delete(synchronize_session=False)
            db.commit()
            print(f"Removed {len(existing_ids)} existing seed user(s) (cascade deleted their data).")

        users = []
        for spec in SEED_USERS:
            user = User(
                name=spec["name"],
                email=spec["email"],
                password_hash=SEED_PASSWORD_HASH,
                role=spec["role"],
            )
            db.add(user)
            users.append(user)
        db.flush()
        print(f"Created {len(users)} users.")

        non_admin_users = [u for u in users if u.role != "admin"]

        conversation_count = 0
        message_count = 0
        issue_count = 0
        rewrite_count = 0

        for user in non_admin_users:
            num_conversations = random.randint(2, 4)

            for _ in range(num_conversations):
                conversation = Conversation(user_id=user.id, status="active")
                db.add(conversation)
                db.flush()
                conversation_count += 1

                num_messages = random.randint(2, 5)
                sample = random.sample(SAMPLE_MESSAGES, k=min(num_messages, len(SAMPLE_MESSAGES)))

                scores_for_avg = []

                for text, score, is_toxic, is_hate, sentiment, issue_type, was_rewritten in sample:
                    analyzed_at = _random_timestamp(days_back=30)

                    message = Message(
                        conversation_id=conversation.id,
                        user_id=user.id,
                        original_text=text,
                        was_rewritten=was_rewritten,
                        created_at=analyzed_at,
                    )
                    db.add(message)
                    db.flush()
                    message_count += 1

                    analysis = MessageAnalysis(
                        message_id=message.id,
                        civility_score=score,
                        toxicity_score=0.85 if is_toxic else round(random.uniform(0.0, 0.15), 4),
                        is_toxic=is_toxic,
                        hate_speech_score=0.8 if is_hate else round(random.uniform(0.0, 0.05), 4),
                        is_hate_speech=is_hate,
                        hate_speech_label="hate" if is_hate else "nothate",
                        sentiment=sentiment,
                        sentiment_confidence=round(random.uniform(0.7, 0.99), 4),
                        llm_is_problematic=issue_type is not None,
                        llm_sentiment=sentiment.lower(),
                        llm_confidence=round(random.uniform(0.7, 0.95), 4),
                        num_tokens=len(text.split()),
                        analyzed_at=analyzed_at,
                    )
                    db.add(analysis)
                    db.flush()
                    scores_for_avg.append(score)

                    if issue_type:
                        db.add(AnalysisIssue(
                            analysis_id=analysis.id,
                            issue_type=issue_type,
                            severity=random.choice(["low", "medium", "high"]),
                            confidence=round(random.uniform(0.6, 0.95), 4),
                            evidence=text[:60],
                        ))
                        issue_count += 1

                        was_accepted = random.choice([True, True, False, None])
                        db.add(RewriteSuggestion(
                            analysis_id=analysis.id,
                            rewrite_text=REWRITE_TEXT.get(issue_type, "Let's discuss this more constructively."),
                            explanation="This message contains language that may come across as hostile.",
                            suggestions=["Focus on the argument, not the person.", "Avoid absolute language."],
                            intent_preserved=True,
                            was_accepted=was_accepted,
                            accepted_at=analyzed_at + timedelta(minutes=2) if was_accepted else None,
                        ))
                        rewrite_count += 1

                conversation.message_count = len(scores_for_avg)
                conversation.avg_civility_score = (
                    round(sum(scores_for_avg) / len(scores_for_avg), 2) if scores_for_avg else None
                )

        db.commit()

        print(f"Created {conversation_count} conversations, {message_count} messages, "
              f"{issue_count} analysis issues, {rewrite_count} rewrite suggestions.")
        print("\nSeed login (any non-admin seed user, or alice.admin@civildialog.seed for admin):")
        print("  password: SeedPassword123!")

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
