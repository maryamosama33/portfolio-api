import asyncio
import httpx

async def get_projects():
    """Get all projects from the portfolio API."""
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/projects")
        response.raise_for_status()
        data = response.json()
        return data["items"]

async def get_skills():
    """Get all skills from the portfolio API."""
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/skills")
        response.raise_for_status()
        data = response.json()
        return data["items"]

async def get_experience():
    """Get all experiences from the portfolio API."""
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/experiences")
        response.raise_for_status()
        data = response.json()
        return data["items"]

async def test_tools():
    print("Testing tools...")
    try:
        projects = await get_projects()
        print(f"Projects: {len(projects)} items")
        print(projects[:2] if projects else "No projects")
    except Exception as e:
        print(f"Projects error: {e}")
    
    try:
        skills = await get_skills()
        print(f"Skills: {len(skills)} items")
        print(skills[:2] if skills else "No skills")
    except Exception as e:
        print(f"Skills error: {e}")
    
    try:
        experiences = await get_experience()
        print(f"Experiences: {len(experiences)} items")
        print(experiences[:2] if experiences else "No experiences")
    except Exception as e:
        print(f"Experiences error: {e}")

if __name__ == "__main__":
    asyncio.run(test_tools())