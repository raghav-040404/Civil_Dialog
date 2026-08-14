from transformers import pipeline

# Loads once when the module is imported — avoids reloading the model on every call
_toxicity_classifier = pipeline(
    "text-classification",
    model="unitary/toxic-bert",
    top_k=None,  # return scores for all labels, not just the top one
)


def detect_toxicity(text: str) -> dict:
    """
    Runs toxicity detection on a piece of text using a pretrained
    Hugging Face model (unitary/toxic-bert).

    Returns a dict like:
    {
        "is_toxic": True,
        "toxicity_score": 0.94,
        "labels": {
            "toxic": 0.94,
            "severe_toxic": 0.12,
            "obscene": 0.55,
            "threat": 0.02,
            "insult": 0.81,
            "identity_hate": 0.03
        }
    }
    """
    results = _toxicity_classifier(text)[0]  # list of {"label": ..., "score": ...}

    labels = {r["label"]: round(r["score"], 4) for r in results}
    toxicity_score = labels.get("toxic", 0.0)

    return {
        "is_toxic": toxicity_score >= 0.5,
        "toxicity_score": toxicity_score,
        "labels": labels,
    }


if __name__ == "__main__":
    sample = "You are stupid. Nobody agrees with you."
    result = detect_toxicity(sample)
    print(result)