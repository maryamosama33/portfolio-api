from app.models.base import BaseDocument

class Experience(BaseDocument):
    title: str
    company: str
    description: str