from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field
from pydantic.alias_generators import to_camel

SITE_DATA_EXAMPLE = {
    "id": 1,
    "title": "Domino Fan Club",
    "prompt": "A website for domino enthusiasts",
    "htmlCodeUrl": "http://example.com/media/index.html",
    "htmlCodeDownloadUrl": "http://example.com/media/index.html?response-content-disposition=attachment",
    "screenshotUrl": "http://example.com/media/index.png",
    "createdAt": "2025-06-15T18:29:56+00:00",
    "updatedAt": "2025-06-15T18:29:56+00:00"
}


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


class CreateSiteRequest(BaseModel):
    title: str | None = Field(default=None, description="Title of the website being created")
    prompt: str = Field(description="Prompt for website generation")

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        json_schema_extra={
            "examples": [
                {
                    "title": "Dominoes fan club",
                    "prompt": "A website for domino enthusiasts"
                }
            ]
        }
    )


class SiteResponse(BaseModel):
    id: int = Field(description="Website ID")
    title: str = Field(description="Website title")
    prompt: str = Field(description="Prompt for website generation")
    html_code_url: str | None = Field(default=None, description="Link to view HTML code")
    html_code_download_url: str | None = Field(default=None, description="File download link")
    screenshot_url: str | None = Field(default=None, description="Link to the website preview screenshot")
    created_at: datetime = Field(description="Website creation date")
    updated_at: datetime = Field(description="Website update date")

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        json_schema_extra={
            "examples": [SITE_DATA_EXAMPLE]
        }
    )


class SiteGenerationRequest(BaseModel):
    prompt: str | None = Field(default=None, description="Prompt for website generation")

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        json_schema_extra={
            "examples": [
                {
                    "prompt": "A website for domino enthusiasts"
                }
            ]
        }
    )


class GeneratedSitesResponse(BaseModel):
    sites: list[SiteResponse] = Field(description="List of all generated websites")

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        json_schema_extra={
            "examples": [
                {
                    "sites": [SITE_DATA_EXAMPLE]
                }
            ]
        }
    )
