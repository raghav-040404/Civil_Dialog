from src.civility import compute_civility_score


def test_civility_returns_dict():
    result = compute_civility_score(
        {"toxicity_score": 0.0},
        {"is_hate_speech": False, "hate_speech_score": 0.0},
        {"has_fallacy": False},
    )
    assert isinstance(result, dict)
    assert "civility_score" in result


def test_civility_perfect_score_for_clean_text():
    result = compute_civility_score(
        {"toxicity_score": 0.0},
        {"is_hate_speech": False, "hate_speech_score": 0.0},
        {"has_fallacy": False},
    )
    assert result["civility_score"] == 100.0


def test_civility_low_score_for_toxic_text():
    result = compute_civility_score(
        {"toxicity_score": 0.9},
        {"is_hate_speech": True, "hate_speech_score": 0.85},
        {"has_fallacy": True},
    )
    assert result["civility_score"] < 20.0