from src.fallacy import detect_fallacy


def test_fallacy_returns_dict():
    result = detect_fallacy("I disagree with your point.")
    assert isinstance(result, dict)
    assert "has_fallacy" in result
    assert "detected_fallacies" in result


def test_fallacy_detects_ad_hominem():
    result = detect_fallacy("You're an idiot, so your argument doesn't matter.")
    assert result["has_fallacy"] is True
    assert "ad hominem" in result["detected_fallacies"]


def test_fallacy_neutral_text():
    result = detect_fallacy("The meeting is scheduled for 3 PM tomorrow.")
    assert result["has_fallacy"] is False
    assert result["detected_fallacies"] == []