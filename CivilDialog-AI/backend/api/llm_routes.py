from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any

from backend.schemas.llm_schema import (
    AnalyzeRequest, AnalyzeResponse,
    RewriteRequest, RewriteResponse,
    FallacyRequest, FallacyResponse,
    FeedbackRequest, FeedbackResponse
)
from backend.services.llm_service import GeminiService
from backend.services.fallacy_service import FallacyService
from backend.services.rewrite_service import RewriteService
from backend.services.feedback_service import FeedbackService
from backend.utils.text_utils import sanitize_text, is_potentially_problematic

router = APIRouter(prefix="/api/v1/llm", tags=["llm"])

# Dependency providers
def get_gemini_service() -> GeminiService:
    return GeminiService()

def get_fallacy_service(gemini: GeminiService = Depends(get_gemini_service)) -> FallacyService:
    return FallacyService(gemini)

def get_rewrite_service(gemini: GeminiService = Depends(get_gemini_service)) -> RewriteService:
    return RewriteService(gemini)

def get_feedback_service() -> FeedbackService:
    return FeedbackService()

@router.post(
    "/analyze", 
    response_model=AnalyzeResponse,
    description="Analyze text for toxicity, personal attacks, hate speech, and logical fallacies, returning a civil rewrite."
)
async def analyze(
    request: AnalyzeRequest,
    gemini_service: GeminiService = Depends(get_gemini_service),
    feedback_service: FeedbackService = Depends(get_feedback_service)
):
    text = request.text
    sanitized = sanitize_text(text)
    
    # 1. Heuristic Pre-screening Check
    # If the text is clearly clean and doesn't trigger any heuristics, bypass LLM
    if not is_potentially_problematic(sanitized):
        return AnalyzeResponse(
            is_problematic=False,
            issues=[],
            sentiment="neutral",
            explanation="The statement is constructive and civil.",
            rewrite=sanitized,
            suggestions=[],
            confidence=1.0
        )
        
    # 2. LLM Analysis Pipeline
    try:
        from backend.services.llm_service import get_prompt_template
        template = get_prompt_template("analysis_prompt.txt")
        prompt = f"Please analyze the following user text according to the rules and schema:\n\nInput Text: {sanitized}"
        
        # Execute structured LLM request
        analysis_result = gemini_service.generate_json_response(
            prompt=prompt,
            system_instruction=template
        )
        
        # Validate format of issues and filter out "none"
        issues = analysis_result.get("issues", [])
        valid_issues = []
        for issue in issues:
            i_type = issue.get("type", "none").strip().lower()
            if i_type != "none" and i_type != "":
                valid_issues.append({
                    "type": i_type,
                    "severity": issue.get("severity", "low").strip().lower(),
                    "confidence": float(issue.get("confidence", 0.8)),
                    "evidence": issue.get("evidence", "").strip()
                })
                
        is_problematic = len(valid_issues) > 0 or analysis_result.get("is_problematic", False)
        
        # Generate suggestions if empty but issues exist
        suggestions = analysis_result.get("suggestions", [])
        if is_problematic and not suggestions:
            # Map feedback suggestions as fallback
            fb = feedback_service.generate_feedback(sanitized, valid_issues)
            suggestions = [fb["improvement_tip"]]
            
        return AnalyzeResponse(
            is_problematic=is_problematic,
            issues=valid_issues,
            sentiment=analysis_result.get("sentiment", "neutral").strip().lower(),
            explanation=analysis_result.get("explanation", "Analysis completed."),
            rewrite=analysis_result.get("rewrite", sanitized),
            suggestions=suggestions,
            confidence=float(analysis_result.get("confidence", 0.8))
        )
        
    except ValueError as ve:
        # Configuration or parsing issue
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        # LLM failure or API timeout
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"LLM service temporarily unavailable: {str(e)}"
        )

@router.post(
    "/rewrite", 
    response_model=RewriteResponse,
    description="Generate a civil, intent-preserving rewrite of a problematic statement."
)
async def rewrite(
    request: RewriteRequest,
    rewrite_service: RewriteService = Depends(get_rewrite_service)
):
    try:
        sanitized = sanitize_text(request.text)
        issues_dict = None
        if request.issues:
            issues_dict = [issue.model_dump() for issue in request.issues]
            
        result = rewrite_service.generate_rewrite(sanitized, issues_dict)
        return RewriteResponse(
            rewrite=result["rewrite"],
            original_intent_preserved=result["original_intent_preserved"]
        )
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
            detail=f"LLM service temporarily unavailable: {str(e)}"
        )

@router.post(
    "/fallacy", 
    response_model=FallacyResponse,
    description="Scan input text and return detected logical fallacies."
)
async def fallacy(
    request: FallacyRequest,
    fallacy_service: FallacyService = Depends(get_fallacy_service)
):
    try:
        sanitized = sanitize_text(request.text)
        detected_fallacies = fallacy_service.detect_fallacies(sanitized)
        return FallacyResponse(fallacies=detected_fallacies)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
            detail=f"LLM service temporarily unavailable: {str(e)}"
        )

@router.post(
    "/feedback", 
    response_model=FeedbackResponse,
    description="Generate detailed feedback and improvement tips for a set of detected issues."
)
async def feedback(
    request: FeedbackRequest,
    feedback_service: FeedbackService = Depends(get_feedback_service)
):
    sanitized = sanitize_text(request.text)
    issues_dict = [issue.model_dump() for issue in request.issues]
    
    result = feedback_service.generate_feedback(sanitized, issues_dict)
    return FeedbackResponse(
        explanation=result["explanation"],
        reason=result["reason"],
        improvement_tip=result["improvement_tip"]
    )

@router.get(
    "/health", 
    description="Retrieve module health status and verify Gemini API key configuration."
)
async def health(gemini_service: GeminiService = Depends(get_gemini_service)):
    # Check if API key is configured
    api_key_configured = gemini_service.api_key is not None
    return {
        "status": "healthy",
        "gemini_api_configured": api_key_configured,
        "model": gemini_service.model_name
    }
