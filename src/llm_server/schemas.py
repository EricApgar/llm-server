from pydantic import BaseModel, Field


class Request(BaseModel):
    tag: str = Field(..., description='Model Identifier/tag (set when hosted), e.g. "Phi-4".')
    prompt: str | dict = Field(..., description='LLM prompt or conversation (llm-conversation.to_dict).')
    images: list[str] | None = Field(default=None, description='Each image should be base64-encoded image bytes.', examples=[None])
    max_tokens: int = Field(default=256, description='Max token count for generation.')
    temperature: float | None = Field(default=None, description='Temperature of generated response.')


class Response(BaseModel):
    text: str