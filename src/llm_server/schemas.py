from pydantic import BaseModel, Field


class Request(BaseModel):
    tag: str = Field(..., description='Model Identifier/tag, e.g. "Phi-4".')
    prompt: str = Field(..., description='LLM prompt.')
    images: list[str]|None = Field(default=None, description='Each image should be base64-encoded image bytes.', examples=[None])
    max_tokens: int = Field(default=256, description='Max token count for generation.')
    temperature: float = Field(default=0.2, description='Temperature of the response.')


class Response(BaseModel):
    text: str