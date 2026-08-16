from src.pipeline import analyze_text


def test_pipeline_returns_full_structure():
    result = analyze_text("Thank you for sharing your perspective.")
    assert isinstance(result, dict)
    for key in ["text", "preprocessing", "toxicity", "hate_speech", "sentiment", "timestamp"]:
        assert key in result


def test_pipeline_detects_toxic_and_negative():
    result = analyze_text("You are stupid. Nobody agrees with you.")
    assert result["toxicity"]["is_toxic"] is True
    assert result["sentiment"]["sentiment"] == "NEGATIVE"


def test_pipeline_detects_civil_and_positive():
    result = analyze_text("I respectfully disagree with your point.")
    assert result["toxicity"]["is_toxic"] is False