from datetime import datetime, timezone

from src.preprocessing import preprocess_text
from src.toxicity import detect_toxicity
from src.hate_speech import detect_hate_speech
from src.sentiment import detect_sentiment


def analyze_text(text: str) -> dict:
    """
    Runs the AI/NLP pipeline on a piece of text:
    preprocessing -> toxicity -> hate speech -> sentiment.

    This is the single entry point the backend team should call.

    Returns:
    {
        "text": "...",
        "preprocessing": {...},
        "toxicity": {...},
        "hate_speech": {...},
        "sentiment": {...},
        "timestamp": "2026-08-14T10:30:00Z"
    }
    """
    preprocessing_result = preprocess_text(text)
    toxicity_result = detect_toxicity(text)
    hate_speech_result = detect_hate_speech(text)
    sentiment_result = detect_sentiment(text)

    return {
        "text": text,
        "preprocessing": preprocessing_result,
        "toxicity": toxicity_result,
        "hate_speech": hate_speech_result,
        "sentiment": sentiment_result,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    sample = "You are stupid. Nobody agrees with you."
    result = analyze_text(sample)
    import json
    print(json.dumps(result, indent=2))