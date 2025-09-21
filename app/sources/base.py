"""Base classes for source adapters."""

from abc import ABC, abstractmethod
from typing import AsyncIterator, Dict, Any


class DiscoveredTool(Dict[str, Any]):
    """Normalized representation of a discovered tool.

    A ``DiscoveredTool`` is a dict with the following keys:

    * ``name`` – Name of the tool (string)
    * ``description`` – Short description (string or None)
    * ``homepage`` – Homepage URL (string or None)
    * ``repo_url`` – Repository URL (string or None)
    * ``language`` – Primary language (string or None)
    * ``tags`` – List of tags (list of strings)
    * ``review`` – A nested dict containing at least the keys
      ``source_url`` (URL string), ``snippet`` (text excerpt),
      and optionally ``published_at`` (ISO datetime string)
    """

    pass


class SourceAdapter(ABC):
    """Abstract base class for all source adapters."""

    @abstractmethod
    async def discover(self) -> AsyncIterator[DiscoveredTool]:
        """Yield normalized tools discovered from this source."""
        raise NotImplementedError