"""Adapter to discover tools from Hacker News."""

import asyncio
import datetime as dt
from typing import AsyncIterator
from .base import SourceAdapter, DiscoveredTool
from ..utils import client

# Official Hacker News Firebase API endpoints
# See https://github.com/HackerNews/API for details
BASE = "https://hacker-news.firebaseio.com/v0"


class HackerNewsAdapter(SourceAdapter):
    """Fetches recent 'Show HN' stories and returns potential tools."""

    def __init__(self, max_items: int = 50) -> None:
        self.max_items = max_items

    async def _get_json(self, url: str):
        async with client() as c:
            r = await c.get(url)
            r.raise_for_status()
            return r.json()

    async def discover(self) -> AsyncIterator[DiscoveredTool]:
        # Get the list of Show HN story IDs
        ids = await self._get_json(f"{BASE}/showstories.json")
        ids = ids[: self.max_items]
        for iid in ids:
            # Fetch each item individually
            item = await self._get_json(f"{BASE}/item/{iid}.json")
            if not item or not item.get("url") or not item.get("title"):
                continue
            # Use the HN title as the name; remove the 'Show HN:' prefix
            name = item["title"].removeprefix("Show HN: ").strip()
            published = dt.datetime.fromtimestamp(
                item.get("time", 0), tz=dt.timezone.utc
            )
            # Yield a normalized tool structure
            yield DiscoveredTool(
                name=name,
                description="Discovered via Show HN.",
                homepage=item.get("url"),
                repo_url=None,
                language=None,
                tags=["hn", "show-hn"],
                review={
                    "source_url": f"https://news.ycombinator.com/item?id={iid}",
                    "snippet": f"{item['title']} (score {item.get('score', 0)}, {item.get('descendants', 0)} comments)",
                    "published_at": published.isoformat(),
                },
            )
            # Small delay between requests to be polite
            await asyncio.sleep(0.1)