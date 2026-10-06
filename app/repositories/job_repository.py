from app.models.job import Job


class JobRepository:
    @staticmethod
    async def create(job: Job) -> Job:
        return await job.insert()

    @staticmethod
    async def existing_urls(urls: list[str]) -> set[str]:
        """Which of `urls` are already stored (deleted ones too, so they don't come back)."""
        if not urls:
            return set()
        jobs = await Job.find({"url": {"$in": urls}}).to_list()
        return {job.url for job in jobs}

    @staticmethod
    async def list_matches(min_score: float | None, limit: int) -> list[Job]:
        """Active jobs, best match first. Unscored jobs sort last."""
        filters: dict = {"is_deleted": {"$ne": True}}
        if min_score is not None:
            filters["match_score"] = {"$gte": min_score}
        return (
            await Job.find(filters)
            .sort([("match_score", -1), ("created_at", -1)])
            .limit(limit)
            .to_list()
        )
