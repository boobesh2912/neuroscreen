"""Authentication schemas."""

from pydantic import BaseModel, Field


class UserRegister(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6)
    email: str = Field(min_length=3)
    first_name: str = Field(min_length=1)
    last_name: str = Field(min_length=1)
    dob: str | None = None
    phone: str | None = None
    address: str | None = None


class UserLogin(BaseModel):
    username: str
    password: str


class UserPublic(BaseModel):
    id: str
    username: str
    email: str
    first_name: str
    last_name: str
    phone_number: str | None = None
    date_of_birth: str | None = None


class LoginResponse(BaseModel):
    success: bool = True
    message: str = "Login successful"
    token: str
    user: UserPublic


class RegisterResponse(BaseModel):
    success: bool = True
    message: str = "Registration successful"
    user_id: str


class VerifyResponse(BaseModel):
    success: bool = True
    user: dict
