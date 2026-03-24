from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    """Schema for creating a new user."""
    email: EmailStr = Field(..., description="User's email address")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    password: str = Field(..., min_length=8, description="Password (minimum 8 characters)")
    full_name: Optional[str] = Field(None, max_length=100, description="User's full name")

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "user@example.com",
                "username": "john_doe",
                "password": "securepass123",
                "full_name": "John Doe"
            }
        }
    }


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, max_length=100)

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "newemail@example.com",
                "full_name": "Jane Doe"
            }
        }
    }


class UserResponse(BaseModel):
    """Schema for user response."""
    id: int = Field(..., description="User ID")
    email: str = Field(..., description="User's email address")
    username: str = Field(..., description="Username")
    full_name: Optional[str] = Field(None, description="User's full name")
    created_at: datetime = Field(..., description="Account creation timestamp")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "username": "john_doe",
                "full_name": "John Doe",
                "created_at": "2026-03-23T10:00:00"
            }
        }
    }
