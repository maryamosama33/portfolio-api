from app.repositories.job_repository import JobRepository
from app.models.skill import Skill
from app.models.experience import Experience
from app.models.project import Project
from tavily import TavilyClient
import os


class JobService:
    @staticmethod
    async def extract_portfolio_skills() -> list[str]:

        skills = await Skill.find_all().to_list()
        return [skill.name.lower() for skill in skills]

    @staticmethod
    async def extract_portfolio_data() -> dict:

        skills = await Skill.find_all().to_list()
        experiences = await Experience.find_all().to_list()
        projects = await Project.find_all().to_list()
        
        return {
            "skills": [skill.name.lower() for skill in skills],
            "experience_titles": [exp.title for exp in experiences] if experiences else [],
            "projects": [proj.name for proj in projects] if projects else [],
        }

    @staticmethod
    async def search_jobs(skills: list[str], max_results: int = 10) -> list[dict]:
        if not skills:
            return []

        client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        query = f"job postings for {' '.join(skills)} developer"
        
        try:
            res = client.search(query=query, max_results=max_results)
            results = res.get("results", [])
            return results
        except Exception as e:
            print(f"Error searching jobs: {e}")
            return []

    @staticmethod
    async def save_jobs(jobs: list[dict], search_query: str, skills: list[str]) -> list[dict]:
        saved_jobs = []
        
        for job_data in jobs:
            if not await JobRepository.exists(job_data.get("url", "")):
                job_dict = {
                    "title": job_data.get("title", ""),
                    "company": job_data.get("source", ""),
                    "url": job_data.get("url", ""),
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
        """Fetch and match jobs based on user's portfolio data.
        
        This method automatically extracts skills, experience, and projects from 
        the database. No external input for skills is accepted.
        
        Returns:
            dict: Result with success status, message, and found jobs
        """
        # Always extract skills from the database
        portfolio_data = await JobService.extract_portfolio_data()
        skills = portfolio_data["skills"]
        
        if not skills:
            return {
                "success": False,
                "message": "No skills found in portfolio",
                "jobs_found": 0,
            }
        
        jobs = await JobService.search_jobs(skills)
        
        if not jobs:
            return {
                "success": False,
                "message": "No jobs found",
                "jobs_found": 0,
            }
        
        query = f"jobs for {' '.join(skills)} developer"
        saved_jobs = await JobService.save_jobs(jobs, query, skills)
        
        return {
            "success": True,
            "message": f"Found {len(saved_jobs)} new jobs",
            "jobs_found": len(saved_jobs),
            "jobs": saved_jobs,
            "portfolio_data": {
                "skills": skills,
                "experience_titles": portfolio_data["experience_titles"],
                "projects": portfolio_data["projects"],
            }
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
