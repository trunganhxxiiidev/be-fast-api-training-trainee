from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(examples=["ok"])


class EchoRequest(BaseModel):
    message: str = Field(min_length=1, examples=["hello FastAPI"])


class EchoResponse(BaseModel):
    echo: str = Field(examples=["hello FastAPI"])
    received_at: str = Field(examples=["2026-06-09T10:30:00.000000+00:00"])


class VersionResponse(BaseModel):
    version: str = Field(examples=["0.1.0"])

