"""
Centralized Civility Score calculation.

This is the single source of truth for the formula. Other modules
(app/services/moderation_service.py) must call calculate_civility_score()
here rather than reimplementing the arithmetic.

CURRENT CANONICAL FORMULA (do not change without an explicit team decision):

    penalty = (toxicity_score * 70) + (hate_speech_score * 30)
    score   = clamp(round(100 - penalty), 0, 100)

This is the formula already live in app/services/moderation_service.py.
It is weighted 70% toxicity / 30% hate speech and produces an integer
0-100 score, where 100 = perfectly civil.

A different, historical formula exists in CivilDialog-AI/src/civility.py
(40% toxicity / 40% hate speech / 20% logical-fallacy-presence, float
0-100 with two-decimal rounding). It was explicitly removed from the
AI/NLP pipeline by Member 3 (commit 335aa78: "remove fallacy/civility
from final pipeline per team scope agreement") and is NOT used here.
"""

CIVILITY_SCORE_VERSION = "1.0.0"

TOXICITY_WEIGHT = 70
HATE_SPEECH_WEIGHT = 30


def calculate_civility_score(
    toxicity_score: float,
    hate_speech_score: float
) -> int:
    """
    Compute the Civility Score (0-100, higher = more civil) from a
    toxicity probability and a hate-speech probability, each expected
    in the [0.0, 1.0] range (as produced by CivilDialog-AI/src/toxicity.py
    and src/hate_speech.py).

    Inputs are clamped to [0.0, 1.0] before use and the result is clamped
    to [0, 100] — this only affects malformed/out-of-range input; for any
    valid probability pair the output is identical to the original
    unclamped formula.
    """

    toxicity = min(max(toxicity_score, 0.0), 1.0)
    hate_speech = min(max(hate_speech_score, 0.0), 1.0)

    penalty = (toxicity * TOXICITY_WEIGHT) + (hate_speech * HATE_SPEECH_WEIGHT)
    score = 100 - penalty

    return max(0, min(100, round(score)))
