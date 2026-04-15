from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.core.config import settings
from app.models.project import Project
from app.models.skill import Skill
from app.models.experience import Experience

async def init_db():
  
    client = AsyncIOMotorClient(settings.mongo_uri)

    db = client[settings.db_name]  

    await init_beanie(
        database=db,
        document_models=[Project, Skill, Experience],
        skip_indexes=True
    )


    