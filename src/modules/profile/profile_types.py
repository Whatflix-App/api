from pydantic import BaseModel, Field


class ProfileResponse(BaseModel):
    id: str
    email: str | None = None
    displayName: str | None = None
    fullName: str | None = None


class UpdateProfileRequest(BaseModel):
    displayName: str | None = Field(default=None, max_length=120)
