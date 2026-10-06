from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings
from app.core.database import init_db
from app.core.exception_handlers import register_exception_handlers
from app.core.logging import setup_logging

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    client = await init_db()
    yield
    await client.close()


app = FastAPI(
    title=settings.app_name,
    description=(
        "Personal portfolio backend with AI job matching (Gemini + Tavily), "
        "a job-description analyzer, and RAG search for the portfolio chatbot."
    ),
    version="2.0.0",
    lifespan=lifespan,
)
app.include_router(api_router)
register_exception_handlers(app)


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}
