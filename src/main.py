from datetime import datetime
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from pydantic.alias_generators import to_camel

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"


class UserDetailsResponse(BaseModel):
    profile_id: int = Field(description="User profile ID")
    username: str = Field(description="User username")
    email: EmailStr = Field(description="User email")
    is_active: bool = Field(description="User status")
    registered_at: datetime = Field(description="User registration date")
    updated_at: datetime = Field(description="Date of last user data update")

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        json_schema_extra={
            "examples": [
                {
                    "profileId": 1,
                    "username": "user123",
                    "email": "example@example.com",
                    "isActive": True,
                    "registeredAt": "2026-09-13T18:29:56+00:00",
                    "updatedAt": "2026-09-15T18:29:56+00:00",
                }
            ]
        },
    )


app = FastAPI(title="AI Website Generator", description="AI-powered website generator built with FastAP.")


@app.get(
    "/users/me",
    summary="Retrieve user credentials",
    response_description="User credentials",
    tags=["Users"],
    response_model=UserDetailsResponse,
)
def get_user():
    mock_user_data = {
        "profileId": 1,
        "username": "user123",
        "email": "example@example.com",
        "isActive": True,
        "registeredAt": "2025-06-15T18:29:56+00:00",
        "updatedAt": "2026-09-15T18:29:56+00:00",
    }
    return mock_user_data


app.mount("/assets", StaticFiles(directory=f"{FRONTEND_DIR}/assets"), name="assets")
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
