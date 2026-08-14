from datetime import datetime, timezone

from src.preprocessing import preprocess_text
from src.toxicity import detect_toxicity
from src.hate_speech import detect_hate_speech
from src.fallacy import detect_fallacy
from src.civility import compute_civility_score


def analyze_text(text: str) -> dict:
    """
    Runs the full AI/NLP pipeline on a piece of text:
    preprocessing -> toxicity -> hate speech -> fallacy -> civility score.

    This is the single entry point the backend team should call.

    Returns:
    {
        "text": "...",
        "preprocessing": {...},
        "toxicity": {...},
        "hate_speech": {...},
        "fallacy": {...},
        "civility_score": 82.4,
        "civility_breakdown": {...},
        "timestamp": "2026-08-14T10:30:00Z"
    }
    """
    preprocessing_result = preprocess_text(text)
    toxicity_result = detect_toxicity(text)
    hate_speech_result = detect_hate_speech(text)
    fallacy_result = detect_fallacy(text)

    civility_result = compute_civility_score(
        toxicity_result, hate_speech_result, fallacy_result
    )

    return {
        "text": text,
        "preprocessing": preprocessing_result,
        "toxicity": toxicity_result,
        "hate_speech": hate_speech_result,
        "fallacy": fallacy_result,
        "civility_score": civility_result["civility_score"],
        "civility_breakdown": civility_result["breakdown"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    sample = "You are stupid. Nobody agrees with you."
    result = analyze_text(sample)
    import json
    print(json.dumps(result, indent=2))