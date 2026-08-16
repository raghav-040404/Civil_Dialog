from src.sentiment import detect_sentiment


def test_sentiment_returns_dict():
    result = detect_sentiment("I love this community.")
    assert isinstance(result, dict)
    assert "sentiment" in result
    assert "confidence" in result


def test_sentiment_detects_negative():
    result = detect_sentiment("You are stupid and everyone hates you.")
    assert result["sentiment"] == "NEGATIVE"


def test_sentiment_detects_positive():
    result = detect_sentiment("I really appreciate your thoughtful perspective.")
    assert result["sentiment"] == "POSITIVE"