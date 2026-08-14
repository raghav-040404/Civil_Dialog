from src.preprocessing import preprocess_text


def test_preprocess_returns_dict():
    result = preprocess_text("I disagree with your argument.")
    assert isinstance(result, dict)
    assert "tokens" in result
    assert result["num_tokens"] > 0


def test_preprocess_tokenizes_correctly():
    result = preprocess_text("Hello world")
    words = [t["text"] for t in result["tokens"]]
    assert "Hello" in words
    assert "world" in words


def test_preprocess_pos_tags_present():
    result = preprocess_text("I disagree with your argument.")
    for token in result["tokens"]:
        assert "pos" in token
        assert token["pos"] != ""