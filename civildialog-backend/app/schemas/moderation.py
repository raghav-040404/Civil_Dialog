from pydantic import BaseModel, Field


class ModerationRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        max_length=5000
    )


class TokenInfo(BaseModel):
    text: str
    lemma: str
    pos: str
    is_stop: bool
    is_punct: bool


class PreprocessingResult(BaseModel):
    original_text: str
    tokens: list[TokenInfo]
    num_tokens: int


class ToxicityResult(BaseModel):
    is_toxic: bool
    toxicity_score: float
    labels: dict[str, float]


class HateSpeechResult(BaseModel):
    is_hate_speech: bool
    hate_speech_score: float
    label: str


class SentimentResult(BaseModel):
    sentiment: str
    confidence: float


class LLMAnalysis(BaseModel):
    is_problematic: bool
    issues: list[dict]
    sentiment: str
    explanation: str
    rewrite: str
    suggestions: list[str]
    confidence: float


class ModerationResult(BaseModel):
    text: str

    preprocessing: PreprocessingResult
    toxicity: ToxicityResult
    hate_speech: HateSpeechResult
    sentiment: SentimentResult

    timestamp: str

    fallacies: list[str]
    feedback: str
    rewrite: str

    llm_analysis: LLMAnalysis

    civility_score: int


class ModerationResponse(BaseModel):
    success: bool
    data: ModerationResult