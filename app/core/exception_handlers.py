from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.exceptions import AIServiceError, NotFoundError, PortfolioIncompleteError


async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"detail": exc.detail, "code": f"{exc.resource.upper()}_NOT_FOUND", "status": 404},
    )


async def ai_service_error_handler(request: Request, exc: AIServiceError) -> JSONResponse:
    return JSONResponse(
        status_code=503,
        content={"detail": exc.detail, "code": "AI_SERVICE_UNAVAILABLE", "status": 503},
    )


async def portfolio_incomplete_handler(request: Request, exc: PortfolioIncompleteError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={"detail": exc.detail, "code": "PORTFOLIO_INCOMPLETE", "status": 422},
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(NotFoundError, not_found_handler)
    app.add_exception_handler(AIServiceError, ai_service_error_handler)
    app.add_exception_handler(PortfolioIncompleteError, portfolio_incomplete_handler)
