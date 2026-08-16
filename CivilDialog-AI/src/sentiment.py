from transformers import pipeline

_sentiment_classifier = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english",
)


def detect_sentiment(text: str) -> dict:
    """
    Runs sentiment analysis on text using a pretrained Hugging Face model.

    Returns a dict like:
    {
        "sentiment": "NEGATIVE",
        "confidence": 0.987
    }
    """
    result = _sentiment_classifier(text)[0]  # {"label": "POSITIVE"/"NEGATIVE", "score": 0.98}

    return {
        "sentiment": result["label"],
        "confidence": round(result["score"], 4),
    }


if __name__ == "__main__":
    sample = "You are stupid. Nobody agrees with you."
    result = detect_sentiment(sample)
    print(result)