"""A read-only snapshot of the whole portfolio, rendered for LLM prompts."""

import asyncio
from dataclasses import dataclass

from app.models.experience import Experience
from app.models.project import Project
from app.models.skill import Skill
from app.repositories.experience_repository import ExperienceRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.skill_repository import SkillRepository

# Higher rank = stronger skill. Unknown levels rank between intermediate and beginner.
_LEVEL_RANK = {"expert": 4, "advanced": 3, "intermediate": 2, "beginner": 0}
_UNKNOWN_LEVEL_RANK = 1


@dataclass
class PortfolioSnapshot:
    skills: list[Skill]
    projects: list[Project]
    experiences: list[Experience]

    @property
    def is_empty(self) -> bool:
        return not (self.skills or self.projects or self.experiences)

    def top_skills(self, n: int) -> list[str]:
        """Skill names, strongest first. Ties keep insertion order."""
        ranked = sorted(
            self.skills,
            key=lambda s: _LEVEL_RANK.get(s.level.strip().lower(), _UNKNOWN_LEVEL_RANK),
            reverse=True,
        )
        return [s.name for s in ranked[:n]]

    def render_profile(self) -> str:
        """Plain-text candidate profile used as LLM context."""
        lines = ["## Skills"]
        lines += [f"- {s.name} ({s.level})" for s in self.skills] or ["- (none listed)"]
        lines.append("\n## Projects")
        lines += [
            f"- {p.name} [{', '.join(p.tech_stack)}]: {p.description}" for p in self.projects
        ] or ["- (none listed)"]
        lines.append("\n## Experience")
        lines += [
            f"- {e.title} at {e.company}: {e.description}" for e in self.experiences
        ] or ["- (none listed)"]
        return "\n".join(lines)


async def load_snapshot() -> PortfolioSnapshot:
    skills, projects, experiences = await asyncio.gather(
        SkillRepository().list_all(),
        ProjectRepository().list_all(),
        ExperienceRepository().list_all(),
    )
    return PortfolioSnapshot(skills=skills, projects=projects, experiences=experiences)
