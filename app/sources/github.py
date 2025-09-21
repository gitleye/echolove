"""Adapter for discovering tools via the GitHub Search API."""

import asyncio
import datetime as dt
import os
from typing import AsyncIterator
from urllib.parse import urlencode
from .base import SourceAdapter, DiscoveredTool
from ..utils import client

# GitHub Search API endpoint
BASE = "https://api.github.com/search/repositories"

# Configuration from environment variables
TOKEN = os.getenv("GITHUB_TOKEN", "")
MIN_STARS = int(os.getenv("MIN_GITHUB_STARS", "10"))
MAX_STARS = int(os.getenv("MAX_GITHUB_STARS", "600"))
ADDED = os.getenv("GITHUB_QUERY_ADDITIONS", "").strip()

# Only include repositories pushed within the last year
PUSHED = (
    dt.datetime.utcnow() - dt.timedelta(days=365)
).date().isoformat()


class GitHubAdapter(SourceAdapter):
    """Searches GitHub for repositories that fit a certain profile."""

    def __init__(self, pages: int = 1) -> None:
        self.pages = pages

    async def discover(self) -> AsyncIterator[DiscoveredTool]:
        # Build the search query
        q_parts = [f"stars:{MIN_STARS}..{MAX_STARS}", f"pushed:>{PUSHED}"]
        if ADDED:
            q_parts.append(f"({ADDED})")
        q = " ".join(q_parts)
        # Authorization header if a token is provided
        headers = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}
        for page in range(1, self.pages + 1):
            qs = {
                "q": q,
                "sort": "stars",
                "order": "desc",
                "per_page": 30,
                "page": page,
            }
            url = f"{BASE}?{urlencode(qs)}"
            async with client() as c:
                r = await c.get(url, headers=headers)
                r.raise_for_status()
                data = r.json()
            for repo in data.get("items", []):
                topics = (
                    ",".join(repo.get("topics", []))
                    if repo.get("topics")
                    else None
                )
                yield DiscoveredTool(
                    name=repo["full_name"],
                    description=repo.get("description"),
                    homepage=repo.get("homepage") or repo.get("html_url"),
                    repo_url=repo.get("html_url"),
                    language=repo.get("language"),
                    tags=topics.split(",") if topics else ["github"],
                    review={
                        "source_url": repo.get("html_url"),
                        "snippet": f"{repo.get('description') or 'No description'} — ⭐ {repo.get('stargazers_count', 0)}",
                        "published_at": None,
                    },
                )
                await asyncio.sleep(0.1)