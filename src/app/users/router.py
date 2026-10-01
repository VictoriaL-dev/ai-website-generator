from fastapi import APIRouter

from app.users.schemas import UserDetailsResponse

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get(
    "/me",
    summary="Retrieve user credentials",
    response_description="User credentials",
    response_model=UserDetailsResponse,
)
async def get_user():
    mock_user_data = {
        "profileId": 1,
        "username": "user123",
        "email": "example@example.com",
        "isActive": True,
        "registeredAt": "2025-06-15T18:29:56+00:00",
        "updatedAt": "2026-09-15T18:29:56+00:00",
    }
    return mock_user_data
