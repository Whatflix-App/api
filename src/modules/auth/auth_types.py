from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class DevicePayload(BaseModel):
    id: str = Field(min_length=1)
    platform: str = Field(min_length=1)
    appVersion: str = Field(min_length=1)


class AppleLoginRequest(BaseModel):
    provider: Literal["apple"]
    identityToken: str = Field(min_length=1)
    authorizationCode: str = Field(min_length=1)
    device: DevicePayload


class AuthUser(BaseModel):
    id: str
    email: str | None = None
    displayName: str | None = None
    authProvider: Literal["apple"]


class TokenPair(BaseModel):
    accessToken: str
    accessTokenExpiresAt: datetime
    refreshToken: str
    refreshTokenExpiresAt: datetime


class AuthSession(BaseModel):
    id: str
    issuedAt: datetime


class AuthSuccessResponse(BaseModel):
    user: AuthUser
    tokens: TokenPair
    session: AuthSession
    isNewUser: bool

    model_config = ConfigDict(from_attributes=True)


class RefreshRequest(BaseModel):
    refreshToken: str = Field(min_length=1)
    sessionId: str = Field(min_length=1)


class RefreshTokensResponse(BaseModel):
    tokens: TokenPair


class LogoutRequest(BaseModel):
    refreshToken: str = Field(min_length=1)
    sessionId: str = Field(min_length=1)
