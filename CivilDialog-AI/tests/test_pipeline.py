from src.pipeline import analyze_text


def test_pipeline_returns_full_structure():
    result = analyze_text("Thank you for sharing your perspective.")
    assert isinstance(result, dict)
    for key in ["text", "preprocessing", "toxicity", "hate_speech", "fallacy", "civility_score", "civility_breakdown", "timestamp"]:
        assert key in result


def test_pipeline_high_civility_for_clean_text():
    result = analyze_text("I respectfully disagree with your point.")
    assert result["civility_score"] > 80


def test_pipeline_low_civility_for_toxic_text():
    result = analyze_text("You are stupid. Nobody agrees with you.")
    assert result["civility_score"] < 60
    assert result["fallacy"]["has_fallacy"] is True