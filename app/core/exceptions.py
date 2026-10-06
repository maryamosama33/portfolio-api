from typing import Any


class NotFoundError(Exception):
    """A requested resource does not exist (or was soft-deleted)."""

    def __init__(self, resource: str, resource_id: Any):
        self.resource = resource
        self.resource_id = str(resource_id)
        self.detail = f"{resource.capitalize()} {resource_id} not found"


class AIServiceError(Exception):
    """An external AI provider (Gemini, Tavily) is unavailable or misconfigured."""

    def __init__(self, detail: str):
        self.detail = detail


class PortfolioIncompleteError(Exception):
    """The portfolio lacks the data an operation needs (e.g. no skills to search with)."""

    def __init__(self, detail: str):
        self.detail = detail
