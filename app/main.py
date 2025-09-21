"""FastAPI application exposing the ECHOLOVE API."""

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional, List
from .db import Base, engine, get_db
from .models import Tool, Review
from .schemas import ToolOut, ReviewOut

# Initialize the FastAPI app
app = FastAPI(title="ECHOLOVE API", version="0.1")
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup() -> None:
    """Create database tables on startup."""
    Base.metadata.create_all(bind=engine)


@app.get("/tools", response_model=List[ToolOut])
def list_tools(
    q: Optional[str] = None,
    tag: Optional[str] = None,
    db: Session = Depends(get_db),
) -> List[Tool]:
    """Return a list of tools, optionally filtered by name or tag.

    Args:
        q: Search query to match against tool names (case insensitive).
        tag: A tag that the tool must include.
        db: Database session (injected).
    """
    stmt = select(Tool).order_by(Tool.updated_at.desc())
    if q:
        stmt = stmt.filter(Tool.name.ilike(f"%{q}%"))
    if tag:
        stmt = stmt.filter(Tool.tags.ilike(f"%{tag}%"))
    tools = db.execute(stmt).scalars().all()
    # Eager load reviews for each tool
    for t in tools:
        _ = t.reviews  # trigger lazy loading
    return tools


@app.get("/tools/{slug}", response_model=ToolOut)
def get_tool(slug: str, db: Session = Depends(get_db)) -> Tool:
    """Retrieve a single tool by slug."""
    tool = db.execute(select(Tool).where(Tool.slug == slug)).scalar_one_or_none()
    if not tool:
        # Use HTTPException for proper 404 response instead of KeyError, which
        # would cause an Internal Server Error. Returning a 404 here makes
        # FastAPI render a helpful error response to the client.
        raise HTTPException(status_code=404, detail="Tool not found")
    _ = tool.reviews
    return tool


@app.get("/reviews", response_model=List[ReviewOut])
def all_reviews(db: Session = Depends(get_db)) -> List[Review]:
    """Return a list of all reviews, ordered by publication date."""
    reviews = db.execute(
        select(Review).order_by(Review.published_at.desc().nullslast())
    ).scalars().all()
    return reviews
