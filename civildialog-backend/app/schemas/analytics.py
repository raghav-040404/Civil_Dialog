from typing import Optional

from pydantic import BaseModel


class OverviewData(BaseModel):
    total_users: int
    total_conversations: int
    total_messages: int
    avg_civility_score: Optional[float]
    toxic_message_count: int
    toxic_message_rate: float
    hate_speech_count: int
    hate_speech_rate: float
    rewrite_offered_count: int
    rewrite_accepted_count: int
    rewrite_adoption_rate: float


class OverviewResponse(BaseModel):
    success: bool
    data: OverviewData


class TrendPoint(BaseModel):
    date: str
    message_count: int
    avg_civility_score: Optional[float]


class TrendResponse(BaseModel):
    success: bool
    data: list[TrendPoint]


class DistributionBucket(BaseModel):
    range: str
    count: int
    percentage: float


class DistributionResponse(BaseModel):
    success: bool
    data: list[DistributionBucket]


class UserSummaryData(BaseModel):
    user_id: int
    message_count: int
    conversation_count: int
    avg_civility_score: Optional[float]
    toxic_count: int
    hate_speech_count: int
    rewrite_count: int
    accepted_rewrite_count: int


class UserSummaryResponse(BaseModel):
    success: bool
    data: UserSummaryData


class ConversationSummaryData(BaseModel):
    conversation_id: int
    message_count: int
    avg_civility_score: Optional[float]
    toxic_count: int
    hate_speech_count: int
    sentiment_distribution: dict[str, int]
    rewrite_count: int


class ConversationSummaryResponse(BaseModel):
    success: bool
    data: ConversationSummaryData


class IssueDistributionItem(BaseModel):
    issue_type: str
    count: int
    percentage: float


class IssueDistributionResponse(BaseModel):
    success: bool
    data: list[IssueDistributionItem]


class RewriteAdoptionData(BaseModel):
    total_suggestions: int
    accepted: int
    rejected: int
    adoption_percentage: float


class RewriteAdoptionResponse(BaseModel):
    success: bool
    data: RewriteAdoptionData


class HistoryMessageItem(BaseModel):
    message_id: int
    conversation_id: int
    original_text: str
    final_text: Optional[str]
    was_rewritten: bool
    created_at: str
    civility_score: Optional[float]
    is_toxic: Optional[bool]
    is_hate_speech: Optional[bool]
    sentiment: Optional[str]


class HistoryData(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[HistoryMessageItem]


class HistoryResponse(BaseModel):
    success: bool
    data: HistoryData
