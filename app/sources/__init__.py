# Package for source adapters.

"""
Adapters for external data sources.

Each adapter implements the ``SourceAdapter`` interface defined in
``base.py`` and yields normalized tool objects via an asynchronous
generator. Adapters included:

* ``hackernews`` – Uses the official Hacker News Firebase API to
  find “Show HN” posts introducing new tools.
* ``stackexchange`` – Queries the Stack Exchange API for recent
  questions that mention tools or software.
* ``github`` – Searches GitHub for repositories within specified star
  ranges and topics, representing under‑the‑radar projects.

To add a new source, create a module implementing the ``SourceAdapter``
class and update the list in ``app/ingest.py``.
"""