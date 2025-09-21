"""SQLAlchemy ORM models for the ECHOLOVE project.

These models represent tools discovered by the ingestion process, the reviews
or mentions from external sources, and the origin of the discovery itself.
"""

from datetime import datetime, timezone
from enum import Enum as PyEnum
from typing import Optional
from sqlalchemy import (
    String,
    Integer,
    Text,
    DateTime,
    Enum,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base


class SourceKind(PyEnum):
    """Enumeration of supported source kinds.

    Each value corresponds to one of the adapters defined under
    ``app/sources``.
    """

    HACKER_NEWS = "hacker_news"
    STACK_EXCHANGE = "stack_exchange"
    GITHUB = "github"


class Tool(Base):
    """Represents a software tool or product discovered by the system."""

    __tablename__ = "tools"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Unique slug generated from the tool name
    slug: Mapped[str] = mapped_column(String(200), unique=True, index=True)

    # Human‑readable name
    name: Mapped[str] = mapped_column(String(300))

    # Optional fields describing the tool
    homepage: Mapped[Optional[str]] = mapped_column(String(2048))
    repo_url: Mapped[Optional[str]] = mapped_column(String(2048))
    description: Mapped[Optional[str]] = mapped_column(Text)
    language: Mapped[Optional[str]] = mapped_column(String(100))
    tags: Mapped[Optional[str]] = mapped_column(String(500))  # comma‑separated tags

    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )

    # Relationships: a tool can have many reviews and origins
    reviews: Mapped[list["Review"]] = relationship(
        back_populates="tool", cascade="all, delete-orphan"
    )
    origins: Mapped[list["Origin"]] = relationship(
        back_populates="tool", cascade="all, delete-orphan"
    )


class Review(Base):
    """Represents a specific mention or review of a tool from a source."""

    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tool_id: Mapped[int] = mapped_column(ForeignKey("tools.id"))
    source_kind: Mapped[SourceKind] = mapped_column(Enum(SourceKind))
    source_url: Mapped[str] = mapped_column(String(2048))
    snippet: Mapped[str] = mapped_column(Text)  # excerpt from the source
    sentiment: Mapped[Optional[str]] = mapped_column(String(20))  # optional sentiment tag
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    last_checked_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(
        String(20), default="active"
    )  # 'active', 'archived', or 'gone'

    # Relationship back to the tool
    tool: Mapped["Tool"] = relationship(back_populates="reviews")


class Origin(Base):
    """Tracks how and when a tool was first discovered."""

    __tablename__ = "origins"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tool_id: Mapped[int] = mapped_column(ForeignKey("tools.id"))
    source_kind: Mapped[SourceKind] = mapped_column(Enum(SourceKind))
    raw_ref: Mapped[str] = mapped_column(String(256))  # stable identifier (e.g., HN ID)
    source_url: Mapped[str] = mapped_column(String(2048))
    discovered_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    # Relationship back to the tool
    tool: Mapped["Tool"] = relationship(back_populates="origins")

    # Ensure we don't create multiple origins for the same source kind and reference
    __table_args__ = (
        UniqueConstraint(
            "source_kind", "raw_ref", name="uq_origin_kind_ref"
        ),
    )