from pydantic import BaseModel
from typing import List, Optional

class MessagePart(BaseModel):
    kind: str
    text: Optional[str] = None
    file_url: Optional[str] = None

class Message(BaseModel):
    kind: str
    role: str
    parts: List[MessagePart]
    messageId: Optional[str] = None
    taskId: Optional[str] = None

class MessageParams(BaseModel):
    message: Message
    configuration: Optional[dict] = None

class A2ARequest(BaseModel):
    jsonrpc: str
    id: str
    method: str
    params: MessageParams
