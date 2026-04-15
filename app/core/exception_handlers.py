from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    ProjectNotFoundError,
    SkillNotFoundError,
    ExperienceNotFoundError
)


async def project_not_found_handler(request: Request, exc: ProjectNotFoundError):

    return JSONResponse(
        status_code=404,
        content={
            "detail": exc.detail,
            "code": "PROJECT_NOT_FOUND",
            "status": 404
        }
    )


async def skill_not_found_handler(request: Request, exc: SkillNotFoundError):

    return JSONResponse(
        status_code=404,
        content={
            "detail": exc.detail,
            "code": "SKILL_NOT_FOUND",
            "status": 404
        }
    )


async def experience_not_found_handler(request: Request, exc: ExperienceNotFoundError):

    return JSONResponse(
        status_code=404,
        content={
            "detail": exc.detail,
            "code": "EXPERIENCE_NOT_FOUND",
            "status": 404
        }
    )