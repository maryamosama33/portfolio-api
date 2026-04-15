from .api_client import fetch

async def get_projects():
    return await fetch("projects")

async def get_skills():
    return await fetch("skills")

async def get_experience():
    return await fetch("experiences")

async def get_summary():
    projects = await fetch("projects")
    skills = await fetch("skills")
    experiences = await fetch("experiences")
    return {
        "total_projects": len(projects),
        "total_skills": len(skills),
        "total_experiences": len(experiences),
        "projects": projects,
        "skills": skills,
        "experiences": experiences
    }