"""Profile-related request schemas."""

from pydantic import BaseModel, ConfigDict, Field


class EmergencyContactCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(min_length=1, max_length=100)
    relationship: str = Field(min_length=1, max_length=100)
    phone: str = Field(alias="phone_number", min_length=3, max_length=30)
    email: str | None = Field(default=None, max_length=254)
    is_primary: bool = False
