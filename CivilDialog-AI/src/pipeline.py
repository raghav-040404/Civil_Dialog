from datetime import datetime, timezone
from typing import Any, Dict, List

from src.preprocessing import preprocess_text
from src.toxicity import detect_toxicity
from src.hate_speech import detect_hate_speech
from src.sentiment import detect_sentiment
from src.fallacy import detect_fallacy
from src.civility import compute_civility_score
from src.llm_client import LLMClient


def _merge_fallacies(
    local_fallacy: Dict[str, Any],
    llm_fallacies: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Merge fast local fallacy detection with
    contextual LLM fallacy detection.

    LLM results are preferred because they contain
    severity, confidence and evidence.
    """

    merged = []

    # ---------------------------------------------------------
    # Add LLM results first
    # ---------------------------------------------------------

    for fallacy in llm_fallacies:

        fallacy_type = str(
            fallacy.get("type", "")
        ).strip().lower()

        if not fallacy_type:
            continue

        merged.append(
            {
                "type": fallacy_type,
                "severity": fallacy.get(
                    "severity",
                    "low",
                ),
                "confidence": fallacy.get(
                    "confidence",
                    0.0,
                ),
                "evidence": fallacy.get(
                    "evidence",
                    "",
                ),
                "source": "llm",
            }
        )

    # ---------------------------------------------------------
    # Add local detections not already detected by LLM
    # ---------------------------------------------------------

    existing_types = {
        item["type"]
        for item in merged
    }

    for local_type in local_fallacy.get(
        "detected_fallacies",
        [],
    ):

        normalized = (
            local_type
            .strip()
            .lower()
            .replace(" ", "_")
        )

        if normalized not in existing_types:

            merged.append(
                {
                    "type": normalized,
                    "severity": "low",
                    "confidence": 0.60,
                    "evidence": "",
                    "source": "local",
                }
            )

    return {
        "has_fallacy": bool(merged),
        "detected_fallacies": [
            item["type"]
            for item in merged
        ],
        "fallacies": merged,
        "local_detection": local_fallacy,
    }


def analyze_text(
    text: str,
    llm_client: LLMClient | None = None,
) -> Dict[str, Any]:
    """
    Complete CivilDialog moderation pipeline.

    Pipeline:

        preprocessing
            ↓
        toxicity
            ↓
        hate speech
            ↓
        sentiment
            ↓
        local fallacy screening
            ↓
        LLM analysis
            ↓
        rewrite / feedback
            ↓
        civility score
    """

    # ---------------------------------------------------------
    # 1. Preprocessing
    # ---------------------------------------------------------

    preprocessing_result = preprocess_text(
        text
    )

    # ---------------------------------------------------------
    # 2. Existing NLP modules
    # ---------------------------------------------------------

    toxicity_result = detect_toxicity(
        text
    )

    hate_speech_result = detect_hate_speech(
        text
    )

    sentiment_result = detect_sentiment(
        text
    )

    # ---------------------------------------------------------
    # 3. Existing local fallacy detection
    # ---------------------------------------------------------

    local_fallacy_result = detect_fallacy(
        text
    )

    # ---------------------------------------------------------
    # 4. LLM integration
    # ---------------------------------------------------------

    llm_result = {
        "available": False,
        "analysis": {},
        "fallacies": [],
        "rewrite": text,
        "feedback": {},
        "error": None,
    }

    if llm_client is None:
        llm_client = LLMClient()

    try:

        # Main LLM analysis
        analysis_result = llm_client.analyze(
            text
        )

        llm_result["analysis"] = (
            analysis_result
        )

        # Use issues from the analysis response
        analysis_issues = analysis_result.get(
            "issues",
            [],
        )

        # The /analyze endpoint already performs
        # contextual fallacy detection as part of
        # the Gemini analysis prompt.

        llm_fallacies = [
            issue
            for issue in analysis_result.get(
                "issues",
                []
            )
            if issue.get("type") in {
                "ad_hominem",
                "strawman",
                "false_dilemma",
                "slippery_slope",
                "hasty_generalization",
                "appeal_to_emotion",
            }
        ]

        llm_result["fallacies"] = llm_fallacies

        # Combine analysis issues + dedicated fallacies
        combined_issues = []

        for issue in analysis_issues:

            if issue.get("type") == "none":
                continue

            combined_issues.append(issue)

        for fallacy in llm_fallacies:

            duplicate = any(
                existing.get("type")
                == fallacy.get("type")
                for existing in combined_issues
            )

            if not duplicate:
                combined_issues.append(
                    fallacy
                )

        # Rewrite only when an issue exists
        if combined_issues:

            rewrite_result = llm_client.rewrite(
                text,
                combined_issues,
            )

            llm_result["rewrite"] = (
                rewrite_result.get(
                    "rewrite",
                    text,
                )
            )

            llm_result[
                "original_intent_preserved"
            ] = rewrite_result.get(
                "original_intent_preserved",
                True,
            )

            # Feedback
            llm_result["feedback"] = (
                llm_client.feedback(
                    text,
                    combined_issues,
                )
            )

        else:

            llm_result["rewrite"] = text

            llm_result[
                "original_intent_preserved"
            ] = True

        llm_result["available"] = True

    except RuntimeError as exc:

        # Graceful degradation:
        # CivilDialog's existing NLP modules
        # continue to work even if Gemini is unavailable.

        llm_result["error"] = str(exc)

    # ---------------------------------------------------------
    # 5. Merge fallacy results
    # ---------------------------------------------------------

    fallacy_result = _merge_fallacies(
        local_fallacy_result,
        llm_result["fallacies"],
    )

    # ---------------------------------------------------------
    # 6. Civility score
    # ---------------------------------------------------------

    civility_result = compute_civility_score(
        toxicity_result=toxicity_result,
        hate_speech_result=hate_speech_result,
        fallacy_result=fallacy_result,
    )

    # ---------------------------------------------------------
    # 7. Final result
    # ---------------------------------------------------------

    return {
        "text": text,

        "preprocessing": (
            preprocessing_result
        ),

        "toxicity": (
            toxicity_result
        ),

        "hate_speech": (
            hate_speech_result
        ),

        "sentiment": (
            sentiment_result
        ),

        "fallacy": (
            fallacy_result
        ),

        "llm": (
            llm_result
        ),

        "civility": (
            civility_result
        ),

        "timestamp": (
            datetime.now(
                timezone.utc
            ).isoformat()
        ),
    }


if __name__ == "__main__":

    import json

    sample = (
        "You are stupid. "
        "Nobody agrees with you."
    )

    result = analyze_text(
        sample
    )

    print(
        json.dumps(
            result,
            indent=2,
        )
    )