from app.services.nlp_service import analyze_nlp
from app.services.llm_service import analyze_with_llm
from app.utils.exceptions import AppException


def calculate_civility_score(
    toxicity: float,
    hate_speech: float
) -> int:
    penalty = (toxicity * 70) + (hate_speech * 30)

    score = 100 - penalty

    return max(0, min(100, round(score)))


async def analyze_text(text: str) -> dict:

    cleaned_text = text.strip()

    if not cleaned_text:
        raise AppException(
            message="Text cannot be empty.",
            code="EMPTY_TEXT",
            status_code=400
        )

    nlp_result = await analyze_nlp(cleaned_text)

    llm_result = await analyze_with_llm(cleaned_text)

    civility_score = calculate_civility_score(
    toxicity=nlp_result["toxicity"]["toxicity_score"],
    hate_speech=nlp_result["hate_speech"]["hate_speech_score"]
)

    return {
        "text": cleaned_text,
        **nlp_result,
        **llm_result,
        "civility_score": civility_score
    }