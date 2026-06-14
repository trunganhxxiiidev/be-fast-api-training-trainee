from pydantic import BaseModel, Field


class EchoRequest(BaseModel):
    message: str = Field(min_length=1, examples=["hello FastAPI"])


class EchoResponse(BaseModel):
    echo: str = Field(examples=["hello FastAPI"])
    received_at: str = Field(examples=["2026-06-09T10:30:00.000000+00:00"])
