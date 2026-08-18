import os
from typing import Any, Dict, List, Optional

import httpx


class LLMClient:
    """
    Client used by CivilDialog-AI to communicate
    with the Member 4 LLM FastAPI service.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: float = 15.0,
    ):
        self.base_url = (
            base_url
            or os.getenv(
                "CIVILDIALOG_LLM_URL",
                "http://127.0.0.1:8000",
            )
        ).rstrip("/")

        self.timeout = timeout

    def _post(
        self,
        endpoint: str,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:

        url = f"{self.base_url}{endpoint}"

        try:
            response = httpx.post(
                url,
                json=payload,
                timeout=self.timeout,
            )

            response.raise_for_status()

            data = response.json()

            if not isinstance(data, dict):
                raise RuntimeError(
                    "LLM service returned an invalid response."
                )

            return data

        except httpx.TimeoutException as exc:
            raise RuntimeError(
                "LLM service request timed out."
            ) from exc

        except httpx.HTTPStatusError as exc:
            raise RuntimeError(
                f"LLM service returned HTTP "
                f"{exc.response.status_code}."
            ) from exc

        except httpx.RequestError as exc:
            raise RuntimeError(
                "Unable to connect to the LLM service."
            ) from exc

        except ValueError as exc:
            raise RuntimeError(
                "LLM service returned invalid JSON."
            ) from exc

    def analyze(self, text: str) -> Dict[str, Any]:
        return self._post(
            "/api/v1/llm/analyze",
            {"text": text},
        )

    def detect_fallacies(
        self,
        text: str,
    ) -> List[Dict[str, Any]]:

        result = self._post(
            "/api/v1/llm/fallacy",
            {"text": text},
        )

        fallacies = result.get(
            "fallacies",
            [],
        )

        return (
            fallacies
            if isinstance(fallacies, list)
            else []
        )

    def rewrite(
        self,
        text: str,
        issues: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:

        payload = {"text": text}

        if issues is not None:
            payload["issues"] = issues

        return self._post(
            "/api/v1/llm/rewrite",
            payload,
        )

    def feedback(
        self,
        text: str,
        issues: List[Dict[str, Any]],
    ) -> Dict[str, Any]:

        return self._post(
            "/api/v1/llm/feedback",
            {
                "text": text,
                "issues": issues,
            },
        )

    def health(self) -> Dict[str, Any]:

        return self._get(
            "/api/v1/llm/health"
        )

    def _get(
        self,
        endpoint: str,
    ) -> Dict[str, Any]:

        url = f"{self.base_url}{endpoint}"

        try:
            response = httpx.get(
                url,
                timeout=self.timeout,
            )

            response.raise_for_status()

            data = response.json()

            if not isinstance(data, dict):
                raise RuntimeError(
                    "LLM service returned an invalid response."
                )

            return data

        except httpx.TimeoutException as exc:
            raise RuntimeError(
                "LLM service request timed out."
            ) from exc

        except httpx.RequestError as exc:
            raise RuntimeError(
                "Unable to connect to the LLM service."
            ) from exc