"""User request/response schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from hlp.models.enums import UserRoleType


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    job_title: str | None = Field(default=None, max_length=255)
    roles: list[UserRoleType] = Field(min_length=1)

    @field_validator("roles")
    @classmethod
    def _dedupe(cls, v: list[UserRoleType]) -> list[UserRoleType]:
        return list(dict.fromkeys(v))


class UserUpdate(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    job_title: str | None = Field(default=None, max_length=255)


class UserRolesUpdate(BaseModel):
    roles: list[UserRoleType] = Field(min_length=1)

    @field_validator("roles")
    @classmethod
    def _dedupe(cls, v: list[UserRoleType]) -> list[UserRoleType]:
        return list(dict.fromkeys(v))


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    profile_id: int
    email: str
    first_name: str
    last_name: str
    job_title: str | None = None
    email_verified: bool
    roles: list[UserRoleType]
    created_at: datetime
