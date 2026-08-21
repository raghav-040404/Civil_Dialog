import pytest
from unittest.mock import MagicMock
from google.genai.errors import APIError
from backend.services.llm_service import GeminiService
from backend.utils.json_parser import parse_json_safely
from backend.utils.text_utils import is_potentially_problematic

def test_gemini_service_initialization():
    service = GeminiService()
    assert service.model_name == "gemini-3.5-flash"
    assert service.api_key == "mock-gemini-key-123456"

def test_gemini_service_client(mock_gemini_client):
    service = GeminiService()
    client = service.client
    assert client is not None

def test_json_parser_clean():
    raw = '{"name": "test"}'
    parsed = parse_json_safely(raw)
    assert parsed == {"name": "test"}

def test_json_parser_markdown():
    raw = '```json\n{"name": "test"}\n```'
    parsed = parse_json_safely(raw)
    assert parsed == {"name": "test"}

def test_json_parser_malformed():
    raw = '{"name": "test",}'
    parsed = parse_json_safely(raw)
    assert parsed == {"name": "test"}

def test_json_parser_invalid():
    raw = 'invalid json'
    parsed = parse_json_safely(raw)
    assert parsed is None

def test_text_heuristics():
    # Constructive/normal inputs should NOT trigger heuristics
    assert not is_potentially_problematic("I think the project needs more testing.")
    assert not is_potentially_problematic("The UI is difficult to navigate because the buttons are not clearly labeled.")
    assert not is_potentially_problematic("I disagree with this proposal because the cost is too high.")
    
    # Toxic/problematic inputs SHOULD trigger heuristics
    assert is_potentially_problematic("You are an idiot.")
    assert is_potentially_problematic("Your project is complete garbage.")
    assert is_potentially_problematic("Either you support this project or you hate the team.")
    assert is_potentially_problematic("Great job breaking the entire application!!!")

def test_api_health(test_client):
    response = test_client.get("/api/v1/llm/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["gemini_api_configured"] is True

def test_api_analyze_normal_constructive(test_client):
    # This should bypass LLM and return is_problematic = False
    response = test_client.post("/api/v1/llm/analyze", json={"text": "I think the project needs more testing."})
    assert response.status_code == 200
    data = response.json()
    assert data["is_problematic"] is False
    assert len(data["issues"]) == 0
    assert data["rewrite"] == "I think the project needs more testing."
    assert data["confidence"] == 1.0

def test_api_analyze_toxic_input(test_client, mock_gemini_client):
    response = test_client.post("/api/v1/llm/analyze", json={"text": "You are stupid and your project is garbage."})
    assert response.status_code == 200
    data = response.json()
    assert data["is_problematic"] is True
    assert len(data["issues"]) > 0
    assert any(i["type"] == "personal_attack" for i in data["issues"])
    assert "rewrite" in data
    assert data["confidence"] > 0.0

def test_api_analyze_validation_empty(test_client):
    response = test_client.post("/api/v1/llm/analyze", json={"text": ""})
    assert response.status_code == 400
    assert response.json()["success"] is False
    assert "empty" in response.json()["error"].lower()

def test_api_analyze_validation_too_short(test_client):
    response = test_client.post("/api/v1/llm/analyze", json={"text": "a"})
    assert response.status_code == 400
    assert response.json()["success"] is False
    assert "at least" in response.json()["error"].lower()

def test_api_analyze_validation_too_long(test_client):
    long_text = "a" * 5001
    response = test_client.post("/api/v1/llm/analyze", json={"text": long_text})
    assert response.status_code == 400
    assert response.json()["success"] is False
    assert "exceeds" in response.json()["error"].lower()

def test_api_analyze_gemini_failure(test_client, mocker):
    # Mock models.generate_content to raise an APIError
    mock_client = mocker.patch("backend.services.llm_service.genai.Client")
    mock_client.return_value.models.generate_content.side_effect = Exception("Gemini server error")

    response = test_client.post("/api/v1/llm/analyze", json={"text": "You are stupid."})
    assert response.status_code == 503
    assert response.json()["success"] is False
    assert "unavailable" in response.json()["error"].lower()
