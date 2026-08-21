import json
import re
from typing import Any, Dict, Optional


def parse_json_safely(raw_text: str) -> Optional[Dict[str, Any]]:
    """
    Safely extracts and parses JSON from LLM output.
    Handles normal JSON, markdown blocks, extra text,
    trailing commas, and common incomplete responses.
    """

    if not raw_text or not isinstance(raw_text, str):
        return None

    text = raw_text.strip()

    # Remove markdown code fences
    code_block_match = re.search(
        r"```(?:json)?\s*(.*?)\s*```",
        text,
        re.DOTALL | re.IGNORECASE,
    )

    if code_block_match:
        text = code_block_match.group(1).strip()

    # Find the beginning of the JSON object
    start_idx = text.find("{")

    if start_idx == -1:
        return None

    text = text[start_idx:].strip()

    # Attempt 1: Normal JSON
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Remove trailing commas
    cleaned_text = re.sub(
        r",\s*([\]}])",
        r"\1",
        text,
    )

    # Attempt 2: Cleaned JSON
    try:
        return json.loads(cleaned_text)
    except json.JSONDecodeError:
        pass

    # Attempt 3: Recover missing closing brace
    recovered = cleaned_text.strip()

    if recovered.startswith("{") and not recovered.endswith("}"):
        recovered += "}"

    try:
        return json.loads(recovered)
    except json.JSONDecodeError:
        return None