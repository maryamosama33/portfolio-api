import re

from app.models.experience import Experience
from app.repositories.base import BaseRepository


class ExperienceRepository(BaseRepository[Experience]):
    model = Experience

    @staticmethod
    def company_filter(company: str | None) -> dict | None:
        """Case-insensitive exact match on company name."""
        if not company:
            return None
        return {"company": {"$regex": rf"^{re.escape(company)}$", "$options": "i"}}
