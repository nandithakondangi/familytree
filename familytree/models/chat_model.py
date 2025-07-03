from pydantic import BaseModel

from familytree.models.base_model import FamilyTreeBaseResponse


class ChatRequest(BaseModel):
    query: str
    conversation_id: str | None = None


class ChatResponse(FamilyTreeBaseResponse):
    response: str
    conversation_id: str
