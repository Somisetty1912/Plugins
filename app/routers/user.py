from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated

from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import UserService

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={
        404: {"description": "User not found"},
        409: {"description": "User already exists"},
    }
)


def get_user_service() -> UserService:
    """Dependency injection for UserService."""
    return UserService()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    responses={
        201: {"description": "User successfully registered"},
        409: {"description": "Email or username already exists"},
    }
)
async def register_user(
    user_data: UserCreate,
    user_service: Annotated[UserService, Depends(get_user_service)]
) -> UserResponse:
    """
    Register a new user.

    - **email**: Must be a valid email address (required)
    - **username**: Between 3 and 50 characters (required)
    - **password**: Minimum 8 characters (required)
    - **full_name**: Optional full name (max 100 characters)

    Returns the created user object with ID and creation timestamp.
    """
    try:
        created_user = user_service.register_user(
            email=user_data.email,
            username=user_data.username,
            password=user_data.password,
            full_name=user_data.full_name
        )
        return UserResponse(**created_user)
    except ValueError as e:
        # Handle business logic validation errors
        error_message = str(e)
        if "already registered" in error_message:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Email already exists"
            )
        elif "already taken" in error_message:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already taken"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message
            )
