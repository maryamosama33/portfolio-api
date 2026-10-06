from fastapi import APIRouter

from app.api.v1 import auth, experiences, jobs, portfolio, projects, skills

api_router = APIRouter(prefix="/api/v1")
for module in (auth, projects, skills, experiences, portfolio, jobs):
    api_router.include_router(module.router)
