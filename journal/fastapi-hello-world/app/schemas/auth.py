from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=12)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
