from app.models.base import BaseDocument

class Skill(BaseDocument):
    name: str
    level: str