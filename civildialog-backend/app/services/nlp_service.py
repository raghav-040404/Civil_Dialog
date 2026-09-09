import asyncio
import sys

from app.core.config import settings


if settings.nlp_module_path not in sys.path:
    sys.path.insert(0, settings.nlp_module_path)


from src.pipeline import analyze_text as analyze_member3_text


async def analyze_nlp(text: str) -> dict:
    """
    Integrates Member 3's AI/NLP pipeline with the FastAPI backend.

    Member 3's pipeline handles:
    - preprocessing
    - toxicity detection
    - hate-speech detection
    - sentiment analysis
    """

    result = await asyncio.to_thread(
        analyze_member3_text,
        text
    )

    return result