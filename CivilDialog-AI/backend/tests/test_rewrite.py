import pytest
from backend.services.rewrite_service import RewriteService
from backend.services.feedback_service import FeedbackService
from backend.services.llm_service import GeminiService

def test_rewrite_service_initialization(mock_gemini_client):
    gemini = GeminiService()
    service = RewriteService(gemini)
    assert service is not None

def test_rewrite_toxic_text(mock_gemini_client):
    gemini = GeminiService()
    service = RewriteService(gemini)
    
    result = service.generate_rewrite("You are stupid.")
    assert "rewrite" in result
    assert result["original_intent_preserved"] is True

def test_rewrite_strawman_text(mock_gemini_client):
    gemini = GeminiService()
    service = RewriteService(gemini)
    
    result = service.generate_rewrite("So you want to eliminate all spending.")
    assert "rewrite" in result
    assert result["original_intent_preserved"] is True

def test_api_rewrite_endpoint(test_client, mock_gemini_client):
    response = test_client.post(
        "/api/v1/llm/rewrite", 
        json={
            "text": "You are stupid.",
            "issues": [{"type": "personal_attack", "severity": "high", "confidence": 0.9, "evidence": "stupid"}]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "rewrite" in data
    assert data["original_intent_preserved"] is True

def test_feedback_service_clean():
    service = FeedbackService()
    fb = service.generate_feedback("I think we need testing.", [])
    assert fb["explanation"] == "No communication issues detected."
    assert "civil" in fb["reason"]

def test_feedback_service_ad_hominem():
    service = FeedbackService()
    issues = [{"type": "ad_hominem", "severity": "high", "confidence": 0.9, "evidence": "idiot"}]
    fb = service.generate_feedback("You are an idiot.", issues)
    assert "Ad Hominem" in fb["explanation"]
    assert "character" in fb["reason"]
    assert "Address the facts" in fb["improvement_tip"]

def test_feedback_service_false_dilemma():
    service = FeedbackService()
    issues = [{"type": "false_dilemma", "severity": "medium", "confidence": 0.8, "evidence": "either/or"}]
    fb = service.generate_feedback("Either support us or leave.", issues)
    assert "False Dilemma" in fb["explanation"]
    assert "oversimplifies" in fb["reason"]

def test_feedback_service_severity_prioritization():
    service = FeedbackService()
    issues = [
        {"type": "toxic_language", "severity": "low", "confidence": 0.8, "evidence": "some bad word"},
        {"type": "ad_hominem", "severity": "high", "confidence": 0.9, "evidence": "idiot"}
    ]
    fb = service.generate_feedback("You are an idiot and this is crap.", issues)
    # High severity ad_hominem should be selected over low severity toxic_language
    assert "Ad Hominem" in fb["explanation"]

def test_feedback_service_fallback():
    service = FeedbackService()
    issues = [{"type": "unknown_issue_type", "severity": "medium", "confidence": 0.8, "evidence": "abc"}]
    fb = service.generate_feedback("Some text.", issues)
    # Should fall back to toxic_language template
    assert "offensive or aggressive" in fb["explanation"]

def test_api_feedback_endpoint(test_client):
    response = test_client.post(
        "/api/v1/llm/feedback",
        json={
            "text": "You are stupid.",
            "issues": [{"type": "personal_attack", "severity": "high", "confidence": 0.94, "evidence": "stupid"}]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "explanation" in data
    assert "reason" in data
    assert "improvement_tip" in data
    assert "personal attack" in data["explanation"].lower()
