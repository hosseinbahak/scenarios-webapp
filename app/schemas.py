from typing import List, Optional, Literal
from pydantic import BaseModel, Field, field_validator

MessageType = Literal["text", "image"]

class Message(BaseModel):
    type: MessageType
    content: str = Field(..., description="text or base64 image")

class ChatRequest(BaseModel):
    chat_id: str
    messages: List<Message]

class ChatResponse(BaseModel):
    message: Optional[str] = None
    base_random_keys: Optional[List[str]] = None
    member_random_keys: Optional[List[str]] = None

    @field_validator("base_random_keys")
    @classmethod
    def cap_base(cls, v):
        return v[:10] if v else v

    @field_validator("member_random_keys")
    @classmethod
    def cap_member(cls, v):
        return v[:10] if v else v
