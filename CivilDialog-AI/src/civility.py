def compute_civility_score(toxicity_result: dict, hate_speech_result: dict, fallacy_result: dict) -> dict:
    """
    Combines toxicity, hate speech, and fallacy detection results
    into a single civility score from 0 (least civil) to 100 (most civil).

    Weighting:
    - Toxicity: 40%
    - Hate speech: 40%
    - Fallacy presence: 20%
    """
    toxicity_score = toxicity_result.get("toxicity_score", 0.0)
    hate_score = hate_speech_result.get("hate_speech_score", 0.0) if hate_speech_result.get("is_hate_speech") else 0.0
    fallacy_penalty = 1.0 if fallacy_result.get("has_fallacy") else 0.0

    # Weighted "incivility" score (0 = perfectly civil, 1 = maximally uncivil)
    incivility = (0.4 * toxicity_score) + (0.4 * hate_score) + (0.2 * fallacy_penalty)
    incivility = min(max(incivility, 0.0), 1.0)  # clamp to [0, 1]

    civility_score = round((1 - incivility) * 100, 2)

    return {
        "civility_score": civility_score,
        "breakdown": {
            "toxicity_contribution": round(0.4 * toxicity_score * 100, 2),
            "hate_speech_contribution": round(0.4 * hate_score * 100, 2),
            "fallacy_contribution": round(0.2 * fallacy_penalty * 100, 2),
        },
    }


if __name__ == "__main__":
    fake_toxicity = {"toxicity_score": 0.9}
    fake_hate = {"is_hate_speech": True, "hate_speech_score": 0.8}
    fake_fallacy = {"has_fallacy": True}

    result = compute_civility_score(fake_toxicity, fake_hate, fake_fallacy)
    print(result)