"""Ingestion script for fetching and storing tool data from external sources."""

import asyncio
import hashlib
from datetime import datetime, timezone
from typing import Optional, Union, List
from sqlalchemy import select
from sqlalchemy.orm import Session
from .db import engine, Base, SessionLocal
from .models import Tool, Review, Origin, SourceKind
from .utils import slugify, head_ok
from .sources.hackernews import HackerNewsAdapter
from .sources.stackexchange import StackExchangeAdapter
from .sources.github import GitHubAdapter


# Register adapters here. Each entry is a tuple of the SourceKind key
# and an instance of the adapter with configuration.
ADAPTERS = [
    ("hacker_news", HackerNewsAdapter(max_items=40)),
    ("stack_exchange", StackExchangeAdapter(pages=1)),
    ("github", GitHubAdapter(pages=1)),
]


def _tags_to_string(tags: Union[List[str], str, None]) -> Optional[str]:
    """Normalize a list of tags into a comma-separated string.

    Accepts a list of strings, a single string, or None. Returns a comma-
    separated string or None. This helper is compatible with Python 3.9
    because it avoids using the ``|`` operator for unions.
    """
    if isinstance(tags, list):
        return ",".join(sorted(set(tags)))
    return tags


def upsert_tool(
    db: Session,
    payload: dict,
    source_kind: SourceKind,
    raw_ref: str,
    source_url: str,
    review: dict,
) -> Tool:
    """Insert or update a tool record, then attach a review and origin."""
    name = payload.get("name") or "Unknown"
    slug = slugify(name)
    tool = db.execute(select(Tool).where(Tool.slug == slug)).scalar_one_or_none()
    now = datetime.now(timezone.utc)

    if not tool:
        # Create a new tool record
        tool = Tool(
            slug=slug,
            name=name,
            description=payload.get("description"),
            homepage=payload.get("homepage"),
            repo_url=payload.get("repo_url"),
            language=payload.get("language"),
            tags=_tags_to_string(payload.get("tags")),
            created_at=now,
            updated_at=now,
        )
        db.add(tool)
        db.flush()
    else:
        # Update fields if they are missing on the existing tool
        tool.description = tool.description or payload.get("description")
        tool.homepage = tool.homepage or payload.get("homepage")
        tool.repo_url = tool.repo_url or payload.get("repo_url")
        tool.language = tool.language or payload.get("language")
        # Merge tags
        if payload.get("tags"):
            existing = set((tool.tags or "").split(",")) if tool.tags else set()
            combined = existing | set(payload["tags"])
            tool.tags = ",".join(sorted(t for t in combined if t))
        tool.updated_at = now

    # Create origin record if this raw reference was not seen before
    exists = db.execute(
        select(Origin).where(
            Origin.source_kind == source_kind, Origin.raw_ref == raw_ref
        )
    ).scalar_one_or_none()
    if not exists:
        db.add(
            Origin(
                tool_id=tool.id,
                source_kind=source_kind,
                raw_ref=raw_ref,
                source_url=source_url,
            )
        )

    # Always add a new review snapshot
    snippet = (review.get("snippet") or "")[:1000]
    # Normalize published_at: if it's a string (ISO 8601), convert to datetime;
    # otherwise pass through (datetime or None). SQLite's DateTime type
    # expects a Python datetime object. This allows adapters to provide either format.
    raw_published = review.get("published_at")
    published_dt = None
    if raw_published:
        if isinstance(raw_published, str):
            try:
                published_dt = datetime.fromisoformat(raw_published)
            except ValueError:
                # If parsing fails, leave as None
                published_dt = None
        else:
            published_dt = raw_published
    db.add(
        Review(
            tool_id=tool.id,
            source_kind=source_kind,
            source_url=source_url,
            snippet=snippet,
            published_at=published_dt,
            last_checked_at=now,
            status="active",
        )
    )
    return tool


async def run_ingest() -> None:
    """Main asynchronous entry point for running the ingestion."""
    Base.metadata.create_all(bind=engine)
    # First pass: discover and insert tools
    with SessionLocal() as db:
        for key, adapter in ADAPTERS:
            kind = SourceKind(key)
            async for item in adapter.discover():
                # Raw reference is a stable hash of the source URL and tool name
                ref = hashlib.sha1(
                    (item["review"]["source_url"] + item["name"]).encode()
                ).hexdigest()[:12]
                upsert_tool(
                    db,
                    item,
                    kind,
                    ref,
                    item["review"]["source_url"],
                    item["review"],
                )
            db.commit()

    # Second pass: check the status of each review's URL
    with SessionLocal() as db:
        for review in db.execute(select(Review)).scalars().all():
            ok = await head_ok(review.source_url)
            review.status = "active" if ok else "archived"
        db.commit()


if __name__ == "__main__":
    asyncio.run(run_ingest())