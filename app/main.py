from fastapi import FastAPI
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from app.core.database import init_db
from app.api.v1 import jobs, projects, skills, experience
from app.core.exception_handlers import experience_not_found_handler, project_not_found_handler, skill_not_found_handler
from app.core.exceptions import ExperienceNotFoundError, ProjectNotFoundError, SkillNotFoundError

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(title="FastAPI Beanie Demo", lifespan=lifespan)

app.include_router(projects.router, tags=["Projects"])
app.include_router(skills.router, tags=["Skills"])
app.include_router(experience.router, tags=["Experiences"])
app.include_router(jobs.router, tags=["Jobs"])

app.add_exception_handler(ProjectNotFoundError, project_not_found_handler)
app.add_exception_handler(SkillNotFoundError, skill_not_found_handler)
app.add_exception_handler(ExperienceNotFoundError, experience_not_found_handler)

@app.get("/health")
async def health():
    return {"status": "ok"}