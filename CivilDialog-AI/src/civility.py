from typing import Any, Dict


def compute_civility_score(
    toxicity_result: Dict[str, Any],
    hate_speech_result: Dict[str, Any],
    fallacy_result: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Combines toxicity, hate speech and logical
    fallacy detection into a 0-100 Civility Score.

    Weighting:
        Toxicity      -> 40%
        Hate speech   -> 40%
        Fallacies     -> 20%

    100 = highly civil
    0   = highly uncivil
    """

    # ---------------------------------------------------------
    # Toxicity
    # ---------------------------------------------------------

    toxicity_score = float(
        toxicity_result.get(
            "toxicity_score",
            0.0,
        )
    )

    toxicity_score = max(
        0.0,
        min(
            toxicity_score,
            1.0,
        ),
    )

    # ---------------------------------------------------------
    # Hate speech
    # ---------------------------------------------------------

    hate_score = 0.0

    if hate_speech_result.get(
        "is_hate_speech",
        False,
    ):

        hate_score = float(
            hate_speech_result.get(
                "hate_speech_score",
                0.0,
            )
        )

    hate_score = max(
        0.0,
        min(
            hate_score,
            1.0,
        ),
    )

    # ---------------------------------------------------------
    # Fallacy
    # ---------------------------------------------------------

    has_fallacy = bool(
        fallacy_result.get(
            "has_fallacy",
            False,
        )
    )

    fallacy_penalty = (
        1.0
        if has_fallacy
        else 0.0
    )

    # ---------------------------------------------------------
    # Weighted score
    # ---------------------------------------------------------

    toxicity_contribution = (
        0.4 * toxicity_score
    )

    hate_contribution = (
        0.4 * hate_score
    )

    fallacy_contribution = (
        0.2 * fallacy_penalty
    )

    incivility = (
        toxicity_contribution
        + hate_contribution
        + fallacy_contribution
    )

    incivility = max(
        0.0,
        min(
            incivility,
            1.0,
        ),
    )

    civility_score = round(
        (1.0 - incivility) * 100,
        2,
    )

    return {
        "civility_score": civility_score,

        "breakdown": {
            "toxicity_contribution": round(
                toxicity_contribution * 100,
                2,
            ),

            "hate_speech_contribution": round(
                hate_contribution * 100,
                2,
            ),

            "fallacy_contribution": round(
                fallacy_contribution * 100,
                2,
            ),
        },
    }