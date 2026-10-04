from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=1, description="User request for image, PDF, or video generation")
    media_type: str | None = Field(default=None, description="Optional force: image, pdf, or video")


class GenerateResponse(BaseModel):
    media_type: str
    prompt: str
    file_path: str
    message: str
