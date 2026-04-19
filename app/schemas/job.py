from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class JobBase(BaseModel):
    title: str
    company: str
    url: str
    snippet: str
    source: str
    matched_skills: List[str] = []
    search_query: str


class JobCreate(JobBase):
    pass


class JobResponse(JobBase):
    id: str
    created_at: datetime
    match_score: Optional[float] = None

    class Config:
        from_attributes = True


class JobListResponse(BaseModel):
    count: int
    jobs: List[JobResponse]


class JobSearchResponse(BaseModel):
    task_id: str
    message: str


class JobSearchResult(BaseModel):
    success: bool
    message: str
    jobs_found: int
    jobs: List[dict] = []
