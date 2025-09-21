"""Adapter for discovering tools via the Stack Exchange API."""

import asyncio
import datetime as dt
from typing import AsyncIterator
from urllib.parse import urlencode
import os
from .base import SourceAdapter, DiscoveredTool
from ..utils import client

# Stack Exchange API v2.3 endpoint
API = "https://api.stackexchange.com/2.3/search"

# Configurable via environment variables
SITES = os.getenv("STACKEXCHANGE_SITES", "stackoverflow").split(";")
KEY = os.getenv("STACKEXCHANGE_KEY", "")


class StackExchangeAdapter(SourceAdapter):
    """Searches Stack Exchange for questions mentioning tools."""

    def __init__(self, pages: int = 1) -> None:
        self.pages = pages

    async def discover(self) -> AsyncIterator[DiscoveredTool]:
        tags = ["tool", "open-source", "productivity"]
        for site in SITES:
            page = 1
            for _ in range(self.pages):
                # Build query params
                qs = {
                    "order": "desc",
                    "sort": "creation",
                    "site": site,
                    "intitle": "recommendation OR tool",
                    "tagged": ";".join(tags),
                    "filter": "default",
                    "pagesize": 20,
                    "page": page,
                }
                if KEY:
                    qs["key"] = KEY
                url = f"{API}?{urlencode(qs)}"
                async with client() as c:
                    r = await c.get(url)
                    r.raise_for_status()
                    data = r.json()
                for q in data.get("items", []):
                    title = q.get("title")
                    link = q.get("link")
                    if not title or not link:
                        continue
                    published = dt.datetime.fromtimestamp(
                        q.get("creation_date", 0), tz=dt.timezone.utc
                    )
                    yield DiscoveredTool(
                        name=title[:100],
                        description=f"Discussed on {site}",
                        homepage=None,
                        repo_url=None,
                        language=None,
                        tags=[site, "stackexchange"],
                        review={
                            "source_url": link,
                            "snippet": title,
                            "published_at": published.isoformat(),
                        },
                    )
                    await asyncio.sleep(0.1)
                # Stop if there are no more pages
                if not data.get("has_more"):
                    break
                page += 1