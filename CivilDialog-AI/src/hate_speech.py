from transformers import pipeline

_hate_speech_classifier = pipeline(
    "text-classification",
    model="facebook/roberta-hate-speech-dynabench-r4-target",
)


def detect_hate_speech(text: str) -> dict:
    """
    Runs hate speech detection using a pretrained Hugging Face model.

    Returns a dict like:
    {
        "is_hate_speech": True,
        "hate_speech_score": 0.87,
        "label": "hate"
    }
    """
    result = _hate_speech_classifier(text)[0]  # {"label": "hate"/"nothate", "score": 0.87}

    is_hate = result["label"].lower() == "hate"

    return {
        "is_hate_speech": is_hate,
        "hate_speech_score": round(result["score"], 4) if is_hate else round(1 - result["score"], 4),
        "label": result["label"],
    }


if __name__ == "__main__":
    sample = "You are stupid. Nobody agrees with you."
    result = detect_hate_speech(sample)
    print(result)