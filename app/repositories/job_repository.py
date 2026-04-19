from app.models.job import Job
from typing import Optional


class JobRepository:
    @staticmethod
    async def create(job_data: dict) -> Job:
        job = Job(**job_data)
        await job.insert()
        return job

    @staticmethod
    async def find_by_id(job_id: str) -> Optional[Job]:
        return await Job.get(job_id)

    @staticmethod
    async def find_by_search_query(search_query: str):
        return await Job.find_many(Job.search_query == search_query, Job.is_deleted == False).to_list()

    @staticmethod
    async def find_recent_jobs(limit: int = 20):
        return await Job.find_many(Job.is_deleted == False).sort([("created_at", -1)]).limit(limit).to_list()

    @staticmethod
    async def find_by_skills(skills: list[str]):
        return await Job.find_many(Job.matched_skills.in_(skills)).to_list()

    @staticmethod
    async def delete_by_search_query(search_query: str):
        jobs = await Job.find_many(Job.search_query == search_query).to_list()
        for job in jobs:
            await job.soft_delete()

    @staticmethod
    async def exists(url: str) -> bool:
        job = await Job.find_one(Job.url == url)
        return job is not None
