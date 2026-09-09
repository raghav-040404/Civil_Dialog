"""
Tests for app/services/civility_service.py.

No database required — pure function tests.
"""

from app.services.civility_service import calculate_civility_score, CIVILITY_SCORE_VERSION


def test_zero_toxicity_and_hate_speech_gives_perfect_score():
    assert calculate_civility_score(0.0, 0.0) == 100


def test_score_decreases_as_toxicity_increases():
    scores = [calculate_civility_score(t, 0.0) for t in (0.0, 0.25, 0.5, 0.75, 1.0)]
    assert scores == sorted(scores, reverse=True)
    assert scores[0] > scores[-1]


def test_score_decreases_as_hate_speech_increases():
    scores = [calculate_civility_score(0.0, h) for h in (0.0, 0.25, 0.5, 0.75, 1.0)]
    assert scores == sorted(scores, reverse=True)
    assert scores[0] > scores[-1]


def test_score_never_goes_below_zero():
    assert calculate_civility_score(1.0, 1.0) == 0
    assert calculate_civility_score(5.0, 5.0) == 0  # out-of-range input, still clamped


def test_score_never_exceeds_100():
    assert calculate_civility_score(0.0, 0.0) == 100
    assert calculate_civility_score(-5.0, -5.0) == 100  # out-of-range input, still clamped


def test_matches_current_canonical_weighting():
    # penalty = toxicity*70 + hate_speech*30
    assert calculate_civility_score(1.0, 0.0) == 30
    assert calculate_civility_score(0.0, 1.0) == 70
    assert calculate_civility_score(0.5, 0.5) == 50


def test_score_is_always_an_int_in_range():
    for t in (0.0, 0.1, 0.33, 0.5, 0.9, 1.0):
        for h in (0.0, 0.1, 0.33, 0.5, 0.9, 1.0):
            score = calculate_civility_score(t, h)
            assert isinstance(score, int)
            assert 0 <= score <= 100


def test_score_version_is_current():
    assert CIVILITY_SCORE_VERSION == "1.0.0"
