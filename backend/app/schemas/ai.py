from typing import Any

from pydantic import BaseModel


class UnderstandRequest(BaseModel):
    text: str


class UnderstandResponse(BaseModel):
    intent: str
    confidence: float
    entities: dict[str, Any]

class ActResponse(BaseModel):
    intent: str
    entities: dict[str, Any]
    result: dict[str, Any]

class ConfirmationRequest(BaseModel):
    action_id: str


class ConfirmationResponse(BaseModel):
    confirmed: bool
    action_id: str
    intent: str
    result: dict[str, Any]