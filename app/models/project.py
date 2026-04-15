from app.models.base import BaseDocument

class Project(BaseDocument):
    name: str
    description: str
    tech_stack: list[str]