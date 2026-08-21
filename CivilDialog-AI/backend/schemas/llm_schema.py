from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from enum import Enum

class IssueType(str, Enum):
    TOXIC_LANGUAGE = "toxic_language"
    HATE_SPEECH = "hate_speech"
    PERSONAL_ATTACK = "personal_attack"
    AD_HOMINEM = "ad_hominem"
    STRAWMAN = "strawman"
    FALSE_DILEMMA = "false_dilemma"
    SLIPPERY_SLOPE = "slippery_slope"
    HASTY_GENERALIZATION = "hasty_generalization"
    APPEAL_TO_EMOTION = "appeal_to_emotion"
    IRRELEVANT_ARGUMENT = "irrelevant_argument"
    NONE = "none"

class SeverityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Issue(BaseModel):
    type: IssueType = Field(..., description="The type of communication issue or logical fallacy detected.")
    severity: SeverityLevel = Field(..., description="The severity of the issue.")
    confidence: float = Field(..., description="Confidence score from 0.0 to 1.0.", ge=0.0, le=1.0)
    evidence: str = Field(..., description="The specific substring of text illustrating the issue.")

class AnalyzeRequest(BaseModel):
    text: str = Field(..., description="The text to analyze.")

    @field_validator("text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        v_stripped = v.strip()
        if not v_stripped:
            raise ValueError("Text cannot be empty or only whitespace.")
        if len(v_stripped) < 2:
            raise ValueError("Text must be at least 2 characters long.")
        if len(v_stripped) > 5000:
            raise ValueError("Text exceeds the limit of 5000 characters.")
        return v_stripped

class AnalyzeResponse(BaseModel):
    is_problematic: bool = Field(..., description="True if issues or fallacies were detected.")
    issues: List[Issue] = Field(default_factory=list, description="List of detected communication issues/fallacies.")
    sentiment: str = Field(..., description="General sentiment of the input text (positive, neutral, negative).")
    explanation: str = Field(..., description="Explanation of why the text is problematic or why it's fine.")
    rewrite: str = Field(..., description="An intent-preserving civil rewrite of the text.")
    suggestions: List[str] = Field(default_factory=list, description="Constructive suggestions for improvement.")
    confidence: float = Field(..., description="Overall confidence of the analysis.", ge=0.0, le=1.0)

class RewriteRequest(BaseModel):
    text: str = Field(..., description="The original text to rewrite.")
    issues: Optional[List[Issue]] = Field(default=None, description="Optional list of previously detected issues to address.")

    @field_validator("text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        v_stripped = v.strip()
        if not v_stripped:
            raise ValueError("Text cannot be empty.")
        if len(v_stripped) > 5000:
            raise ValueError("Text exceeds 5000 characters.")
        return v_stripped

class RewriteResponse(BaseModel):
    rewrite: str = Field(..., description="The respectful, intent-preserving rewrite.")
    original_intent_preserved: bool = Field(True, description="Indicates whether the rewrite successfully preserved the user's intent.")

class FallacyRequest(BaseModel):
    text: str = Field(..., description="The text to scan for logical fallacies.")

    @field_validator("text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        v_stripped = v.strip()
        if not v_stripped:
            raise ValueError("Text cannot be empty.")
        if len(v_stripped) > 5000:
            raise ValueError("Text exceeds 5000 characters.")
        return v_stripped

class FallacyResponse(BaseModel):
    fallacies: List[Issue] = Field(..., description="List of detected logical fallacies.")

class FeedbackRequest(BaseModel):
    text: str = Field(..., description="The original text.")
    issues: List[Issue] = Field(..., description="List of issues detected in the text.")

    @field_validator("text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Text cannot be empty.")
        return v.strip()

class FeedbackResponse(BaseModel):
    explanation: str = Field(..., description="Description of the communication issue.")
    reason: str = Field(..., description="Why this statement is problematic.")
    improvement_tip: str = Field(..., description="Tip on how to construct a better response next time.")
