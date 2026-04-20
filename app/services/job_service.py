from app.repositories.job_repository import JobRepository
from app.models.skill import Skill
from app.models.experience import Experience
from app.models.project import Project
from tavily import TavilyClient
import os


class JobService:

    @staticmethod
    async def extract_portfolio_data() -> dict:
        skills = await Skill.find_all().to_list()
        experiences = await Experience.find_all().to_list()
        projects = await Project.find_all().to_list()

        return {
            "skills": [skill.name.lower() for skill in skills],
            "experience_titles": [exp.title.lower() for exp in experiences] if experiences else [],
            "projects": [proj.name.lower() for proj in projects] if projects else [],
        }

    @staticmethod
    def build_search_query(portfolio_data: dict) -> str:
        skills = portfolio_data.get("skills", [])
        experiences = portfolio_data.get("experience_titles", [])
        projects = portfolio_data.get("projects", [])

        query_parts = []

        if skills:
            query_parts.append(f"{' '.join(skills)} developer")

        if experiences:
            query_parts.append(f"experience in {' '.join(experiences)}")

        if projects:
            query_parts.append(f"projects like {' '.join(projects)}")

        final_query = "job postings for " + " ".join(query_parts)

        return final_query.strip()

    @staticmethod
    async def search_jobs(query: str, max_results: int = 10) -> list[dict]:
        if not query:
            return []

        client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

        try:
            res = client.search(query=query, max_results=max_results)
            return res.get("results", [])
        except Exception as e:
            print(f"Error searching jobs: {e}")
            return []

    @staticmethod
    async def save_jobs(jobs: list[dict], search_query: str, skills: list[str]) -> list[dict]:
        saved_jobs = []

        for job_data in jobs:
            url = job_data.get("url", "")

            if not url:
                continue

            if not await JobRepository.exists(url):
                job_dict = {
                    "title": job_data.get("title", ""),
                    "company": job_data.get("source", ""),
                    "url": url,
                    "snippet": job_data.get("snippet", ""),
                    "source": job_data.get("source", ""),
                    "matched_skills": skills,
                    "search_query": search_query,
                    "match_score": None,
                }

                try:
                    saved_job = await JobRepository.create(job_dict)
                    saved_jobs.append({
                        "id": str(saved_job.id),
                        "title": saved_job.title,
                        "company": saved_job.company,
                        "url": saved_job.url,
                        "matched_skills": saved_job.matched_skills,
                    })
                except Exception as e:
                    print(f"Error saving job: {e}")

        return saved_jobs

    @staticmethod
    async def fetch_and_match_jobs() -> dict:
        portfolio_data = await JobService.extract_portfolio_data()

        skills = portfolio_data["skills"]

        if not skills:
            return {
                "success": False,
                "message": "No skills found in portfolio",
                "jobs_found": 0,
            }

        query = JobService.build_search_query(portfolio_data)

        jobs = await JobService.search_jobs(query)

        if not jobs:
            return {
                "success": False,
                "message": "No jobs found",
                "jobs_found": 0,
            }

        saved_jobs = await JobService.save_jobs(jobs, query, skills)

        return {
            "success": True,
            "message": f"Found {len(saved_jobs)} new jobs",
            "jobs_found": len(saved_jobs),
            "jobs": saved_jobs,
            "portfolio_data": portfolio_data,
            "search_query": query,  
        }

    @staticmethod
    async def get_recent_jobs(limit: int = 20) -> list[dict]:
        jobs = await JobRepository.find_recent_jobs(limit)

        return [
            {
                "id": str(job.id),
                "title": job.title,
                "company": job.company,
                "url": job.url,
                "matched_skills": job.matched_skills,
                "search_query": job.search_query,
                "created_at": job.created_at,
            }
            for job in jobs
        ]