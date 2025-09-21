"""Pydantic models for API responses.

These schemas translate SQLAlchemy models into JSON-friendly structures
for FastAPI responses. They avoid leaking internal database state and
provide type hints for clients consuming the API.
"""

from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, HttpUrl, ConfigDict
from .models import SourceKind


class ReviewOut(BaseModel):
    """Schema representing a review record returned by the API."""

    source_kind: SourceKind
    source_url: HttpUrl
    snippet: str
    published_at: Optional[datetime]
    status: Literal["active", "archived", "gone"]
    # Pydantic configuration: treat enums as their values and enable ORM mode
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

class ToolOut(BaseModel):
    """Schema representing a tool with nested reviews."""

    slug: str
    name: str
    description: Optional[str]
    homepage: Optional[str]
    repo_url: Optional[str]
    language: Optional[str]
    tags: Optional[str]
    reviews: List[ReviewOut] = []
    # Enable ORM mode for nested models
    model_config = ConfigDict(from_attributes=True)