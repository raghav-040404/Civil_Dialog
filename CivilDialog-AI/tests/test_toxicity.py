from src.toxicity import detect_toxicity


def test_toxicity_returns_dict():
    result = detect_toxicity("You are stupid.")
    assert isinstance(result, dict)
    assert "is_toxic" in result
    assert "toxicity_score" in result
    assert "labels" in result


def test_toxicity_detects_toxic_text():
    result = detect_toxicity("You are a worthless idiot and everyone hates you.")
    assert result["is_toxic"] is True
    assert result["toxicity_score"] > 0.5


def test_toxicity_allows_civil_text():
    result = detect_toxicity("I respectfully disagree with your point.")
    assert result["is_toxic"] is False