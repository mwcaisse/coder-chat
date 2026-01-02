import uuid

from pydantic import BaseModel, Field, field_validator


class CreateNewUserModel(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=8)
    name: str = Field(min_length=1, max_length=100)

    @field_validator("email", mode="after")
    @classmethod
    def is_email(cls, value: str) -> str:
        if "@" in value:
            return value

        raise ValueError("Invalid email, must contain @")


class UserLoginModel(BaseModel):
    username: str
    password: str


class UserTokenLoginModel(BaseModel):
    username: str
    refresh_token: str


class UserLoginResponse(BaseModel):
    access_token: str
    refresh_token: str


class UserResponse(BaseModel):
    id: uuid.UUID
    username: str
    name: str
    email: str
