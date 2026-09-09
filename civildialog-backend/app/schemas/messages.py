from pydantic import BaseModel


class AcceptRewriteData(BaseModel):
    message_id: int
    rewrite_suggestion_id: int
    final_text: str
    was_rewritten: bool
    was_accepted: bool
    accepted_at: str


class AcceptRewriteResponse(BaseModel):
    success: bool
    data: AcceptRewriteData
