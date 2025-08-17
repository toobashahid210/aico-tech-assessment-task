from typing import Optional
from pydantic import BaseModel, HttpUrl

class SummarizeRequest(BaseModel):
    url: HttpUrl

class ChatRequest(BaseModel):
    question: str
    session_id: Optional[str] = None
    