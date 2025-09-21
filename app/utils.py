"""Utility functions used across the ECHOLOVE project."""

import asyncio
import hashlib
from contextlib import asynccontextmanager
import re
from typing import AsyncGenerator
import httpx


# Default User-Agent for outbound HTTP requests
USER_AGENT = "ECHOLOVE/0.1 (+https://example.com)"


def slugify(name: str) -> str:
    """Return a URL-friendly slug generated from a name.

    Non-alphanumeric characters are replaced with hyphens, leading and
    trailing hyphens are removed, and if the result is empty the slug
    becomes a short SHA1 digest of the original string.
    """
    s = re.sub(r"[^a-zA-Z0-9]+", "-", name.strip().lower()).strip("-")
    if not s:
        s = hashlib.sha1(name.encode()).hexdigest()[:8]
    return s


@asynccontextmanager
async def client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """Provide a configured AsyncClient for HTTP requests.

    This helper centralizes the User-Agent header and timeout settings.
    """
    headers = {"User-Agent": USER_AGENT}
    timeout = httpx.Timeout(15.0, connect=10.0)
    async with httpx.AsyncClient(
        headers=headers, timeout=timeout, follow_redirects=True
    ) as c:
        yield c


async def head_ok(url: str) -> bool:
    """Check whether a URL is reachable via a HEAD request.

    Returns True if the request succeeds with a status code < 400,
    otherwise returns False. Any exception results in False.
    """
    try:
        async with client() as c:
            r = await c.head(url)
            return r.status_code < 400
    except Exception:
        return False