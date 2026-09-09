import httpx

from app.core.config import settings


LOGICAL_FALLACY_TYPES = {
    "ad_hominem",
    "strawman",
    "false_dilemma",
    "slippery_slope",
    "hasty_generalization",
    "appeal_to_emotion",
    "irrelevant_argument",
}


async def analyze_with_llm(text: str) -> dict:
    """
    Calls Member 4's standalone LLM service and adapts
    its response to the main backend response structure.
    """

    url = f"{settings.llm_service_url}/api/v1/llm/analyze"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                url,
                json={"text": text}
            )

            response.raise_for_status()

            result = response.json()

    except httpx.TimeoutException as exc:
        raise RuntimeError(
            "LLM service request timed out."
        ) from exc

    except httpx.HTTPStatusError as exc:
        raise RuntimeError(
            f"LLM service returned HTTP {exc.response.status_code}."
        ) from exc

    except httpx.RequestError as exc:
        raise RuntimeError(
            "Could not connect to LLM service."
        ) from exc

    issues = result.get("issues", [])

    fallacies = [
        issue["type"]
        for issue in issues
        if issue.get("type") in LOGICAL_FALLACY_TYPES
    ]

    return {
        # Existing main-backend fields
        "fallacies": fallacies,
        "feedback": result.get("explanation", ""),
        "rewrite": result.get("rewrite", ""),

        # Complete Member 4 analysis
        "llm_analysis": result
    }