"""Tools the chatbot agent can call. Docstrings are what the LLM reads to choose a tool."""

from .api_client import get_json

LIST_PAGE_SIZE = 50


async def search_portfolio(query: str) -> list[dict]:
    """Semantic search over Maryam's projects, skills and experience.

    Use this first for any specific question, e.g. "has she used Docker?",
    "what AI projects has she built?", "is she a fit for a backend role?".

    Args:
        query: The user's question or the topic to look up, in natural language.

    Returns:
        The most relevant portfolio entries, best match first. Each has
        `source_type` (project/skill/experience), `text` and a relevance `score`.
    """
    data = await get_json("/portfolio/search", params={"q": query, "k": 6})
    return data["results"] if data else []


async def list_projects() -> list[dict]:
    """List every project. Use only when the user asks for all projects or an overview."""
    data = await get_json("/projects", params={"size": LIST_PAGE_SIZE})
    return data["items"] if data else []


async def list_skills() -> list[dict]:
    """List every skill with its level. Use only when the user asks for all skills."""
    data = await get_json("/skills", params={"size": LIST_PAGE_SIZE})
    return data["items"] if data else []


async def list_experience() -> list[dict]:
    """List all work experience. Use only when the user asks for her full work history."""
    data = await get_json("/experiences", params={"size": LIST_PAGE_SIZE})
    return data["items"] if data else []
