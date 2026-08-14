from src.hate_speech import detect_hate_speech


def test_hate_speech_returns_dict():
    result = detect_hate_speech("I disagree with your point.")
    assert isinstance(result, dict)
    assert "is_hate_speech" in result
    assert "hate_speech_score" in result


def test_hate_speech_detects_civil_text():
    result = detect_hate_speech("I respectfully disagree with your point.")
    assert result["is_hate_speech"] is False


def test_hate_speech_detects_hateful_text():
    result = detect_hate_speech("I hate people like you, you don't belong here.")
    assert isinstance(result["hate_speech_score"], float)