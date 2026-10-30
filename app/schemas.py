from pydantic import BaseModel, Field

class AskRequest(BaseModel):
    question: str = Field(min_length=5, max_length=2000)

class AgentResponse(BaseModel):
    status: str
    question: str
    answer: str
    sources: list[str] = []
    disclaimer: str
