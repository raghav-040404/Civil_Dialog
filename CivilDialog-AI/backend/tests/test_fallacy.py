import pytest
from backend.services.fallacy_service import FallacyService
from backend.services.llm_service import GeminiService

def test_fallacy_service_initialization(mock_gemini_client):
    gemini = GeminiService()
    service = FallacyService(gemini)
    assert service is not None

def test_fallacy_detection_clean(mock_gemini_client):
    gemini = GeminiService()
    service = FallacyService(gemini)
    
    # "I think the project needs more testing." is constructive criticism and has no fallacy
    fallacies = service.detect_fallacies("I think the project needs more testing.")
    assert len(fallacies) == 0

def test_fallacy_detection_ad_hominem(mock_gemini_client):
    gemini = GeminiService()
    service = FallacyService(gemini)
    
    fallacies = service.detect_fallacies("Don't trust his argument because he is stupid.")
    assert len(fallacies) > 0
    assert any(f["type"] == "ad_hominem" for f in fallacies)
    assert "stupid" in fallacies[0]["evidence"] or "idiot" in fallacies[0]["evidence"]

def test_fallacy_detection_strawman(mock_gemini_client):
    gemini = GeminiService()
    service = FallacyService(gemini)
    
    fallacies = service.detect_fallacies("You want to reduce spending, so you want to eliminate all spending.")
    assert len(fallacies) > 0
    assert any(f["type"] == "strawman" for f in fallacies)

def test_fallacy_detection_false_dilemma(mock_gemini_client):
    gemini = GeminiService()
    service = FallacyService(gemini)
    
    fallacies = service.detect_fallacies("Either you support this project or you don't care about the team.")
    assert len(fallacies) > 0
    assert any(f["type"] == "false_dilemma" for f in fallacies)

def test_fallacy_detection_slippery_slope(mock_gemini_client):
    gemini = GeminiService()
    service = FallacyService(gemini)
    
    fallacies = service.detect_fallacies("If we allow one late submission, eventually nobody will meet deadlines.")
    assert len(fallacies) > 0
    assert any(f["type"] == "slippery_slope" for f in fallacies)

def test_fallacy_detection_hasty_generalization(mock_gemini_client):
    gemini = GeminiService()
    service = FallacyService(gemini)
    
    fallacies = service.detect_fallacies("Two students cheated, so all students are dishonest.")
    assert len(fallacies) > 0
    assert any(f["type"] == "hasty_generalization" for f in fallacies)

def test_fallacy_detection_appeal_to_emotion(mock_gemini_client):
    gemini = GeminiService()
    service = FallacyService(gemini)
    
    fallacies = service.detect_fallacies("You should agree with me because otherwise you'll make me feel terrible.")
    assert len(fallacies) > 0
    assert any(f["type"] == "appeal_to_emotion" for f in fallacies)

def test_api_fallacy_endpoint(test_client, mock_gemini_client):
    response = test_client.post("/api/v1/llm/fallacy", json={"text": "Either you support this project or you don't care about the team."})
    assert response.status_code == 200
    data = response.json()
    assert "fallacies" in data
    assert len(data["fallacies"]) > 0
    assert data["fallacies"][0]["type"] == "false_dilemma"

def test_api_fallacy_endpoint_clean(test_client, mock_gemini_client):
    # Heuristics bypass check: is_potentially_problematic is False -> returns clean or goes through service
    # Wait, for the fallacy endpoint, does it use the fallacy service? Yes. And the mock gemini client returns empty
    response = test_client.post("/api/v1/llm/fallacy", json={"text": "I think the project needs more testing."})
    assert response.status_code == 200
    data = response.json()
    assert "fallacies" in data
    assert len(data["fallacies"]) == 0
