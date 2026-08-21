import os
import json
import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

# Set up mock environment variables prior to application import
os.environ["GEMINI_API_KEY"] = "mock-gemini-key-123456"
os.environ["GEMINI_MODEL"] = "gemini-3.5-flash"

from backend.main import app

@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.fixture
def mock_gemini_client(mocker):
    """
    Mocks the official Google GenAI Client and patches models.generate_content
    to return realistic structured JSON response data based on the input text.
    """
    mock_client_cls = mocker.patch("backend.services.llm_service.genai.Client")
    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client

    def mock_generate_content(model, contents, config):
        prompt_lower = contents.lower()
        system_instr = str(config.system_instruction or "").lower() if config else ""

        # Default Response
        response_data = {
            "is_problematic": False,
            "issues": [],
            "sentiment": "neutral",
            "explanation": "The statement is civil and constructive.",
            "rewrite": contents,
            "suggestions": [],
            "confidence": 1.0
        }

        # Ad Hominem & Personal Attack
        if "idiot" in prompt_lower or "stupid" in prompt_lower or "garbage" in prompt_lower or "trash" in prompt_lower:
            response_data = {
                "is_problematic": True,
                "issues": [
                    {
                        "type": "personal_attack",
                        "severity": "high",
                        "confidence": 0.94,
                        "evidence": "idiot" if "idiot" in prompt_lower else "stupid"
                    },
                    {
                        "type": "ad_hominem",
                        "severity": "high",
                        "confidence": 0.92,
                        "evidence": "you are stupid" or "you are an idiot"
                    }
                ],
                "sentiment": "negative",
                "explanation": "Attacks the person directly rather than discussing the proposal.",
                "rewrite": "I disagree with this project because I believe it has several limitations.",
                "suggestions": ["Focus on the argument instead of criticizing the person."],
                "confidence": 0.93
            }

        # Strawman
        elif "spending" in prompt_lower or "eliminate all" in prompt_lower:
            response_data = {
                "is_problematic": True,
                "issues": [
                    {
                        "type": "strawman",
                        "severity": "medium",
                        "confidence": 0.88,
                        "evidence": "eliminate all spending" or "stop spending money completely"
                    }
                ],
                "sentiment": "negative",
                "explanation": "Misrepresents the opponent's argument to make it easier to attack.",
                "rewrite": "I understand you want to reduce expenses, but we should make sure we don't cut essential operations.",
                "suggestions": ["Accurately restate the opposing argument before criticizing it."],
                "confidence": 0.90
            }

        # False Dilemma
        elif "either" in prompt_lower or "or you" in prompt_lower:
            response_data = {
                "is_problematic": True,
                "issues": [
                    {
                        "type": "false_dilemma",
                        "severity": "high",
                        "confidence": 0.89,
                        "evidence": "either you agree with me or you hate the project"
                    }
                ],
                "sentiment": "negative",
                "explanation": "Over-simplifies the situation by offering only two extreme alternatives.",
                "rewrite": "I disagree with this part of the proposal, although there are other aspects I support.",
                "suggestions": ["Acknowledge that there are intermediate or alternative choices available."],
                "confidence": 0.91
            }

        # Slippery Slope
        elif "collapse" in prompt_lower or "exception" in prompt_lower or "late submission" in prompt_lower:
            response_data = {
                "is_problematic": True,
                "issues": [
                    {
                        "type": "slippery_slope",
                        "severity": "medium",
                        "confidence": 0.85,
                        "evidence": "everything will collapse" or "eventually nobody will meet deadlines"
                    }
                ],
                "sentiment": "negative",
                "explanation": "Assumes a chain of extreme consequences without sufficient backing.",
                "rewrite": "If we accept this late submission, let's establish a clear policy to ensure it remains a rare exception.",
                "suggestions": ["Connect actions to their consequences with logic and evidence rather than assumptions."],
                "confidence": 0.87
            }

        # Hasty Generalization
        elif "cheated" in prompt_lower or "everyone cheats" in prompt_lower:
            response_data = {
                "is_problematic": True,
                "issues": [
                    {
                        "type": "hasty_generalization",
                        "severity": "medium",
                        "confidence": 0.86,
                        "evidence": "all students are dishonest" or "everyone cheats"
                    }
                ],
                "sentiment": "negative",
                "explanation": "Draws a broad conclusion from a very small and non-representative sample.",
                "rewrite": "Because a few students cheated, we should look into why that happened without generalizing to the entire student body.",
                "suggestions": ["Qualify the scope of your claims using words like 'some' rather than 'all'."],
                "confidence": 0.88
            }

        # Appeal to Emotion
        elif "feel terrible" in prompt_lower or "make me" in prompt_lower or "sad" in prompt_lower:
            response_data = {
                "is_problematic": True,
                "issues": [
                    {
                        "type": "appeal_to_emotion",
                        "severity": "medium",
                        "confidence": 0.83,
                        "evidence": "make me feel terrible"
                    }
                ],
                "sentiment": "neutral",
                "explanation": "Relies primarily on emotional manipulation instead of logic.",
                "rewrite": "I hope we can reconsider this plan as it is very important to my workflow.",
                "suggestions": ["Support arguments with logic and evidence rather than appeals to emotion."],
                "confidence": 0.85
            }

        # Sarcasm
        elif "great job breaking" in prompt_lower:
            response_data = {
                "is_problematic": True,
                "issues": [
                    {
                        "type": "toxic_language",
                        "severity": "low",
                        "confidence": 0.78,
                        "evidence": "Great job breaking the entire application"
                    }
                ],
                "sentiment": "negative",
                "explanation": "Uses sarcastic and passive-aggressive framing.",
                "rewrite": "The recent update caused the application to crash. We should investigate and fix it.",
                "suggestions": ["Express criticisms directly and constructively, avoiding sarcasm."],
                "confidence": 0.80
            }

        # Check if the system instruction or prompt is specific to fallacy_prompt.txt
        if "logical fallacy detection" in system_instr or "fallacy_prompt.txt" in system_instr or "fallacies" in prompt_lower:
            return MagicMock(text=json.dumps({"fallacies": response_data["issues"]}))

        # Check if the system instruction or prompt is specific to rewrite_prompt.txt
        if "intent-preserving rewrite" in system_instr or "rewrite_prompt.txt" in system_instr or "generate_rewrite" in prompt_lower:
            return MagicMock(text=json.dumps({
                "rewrite": response_data["rewrite"],
                "original_intent_preserved": True
            }))

        # Otherwise return full analysis response
        mock_response = MagicMock()
        mock_response.text = json.dumps(response_data)
        return mock_response

    mock_client.models.generate_content.side_effect = mock_generate_content
    return mock_client
