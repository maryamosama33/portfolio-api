class ProjectNotFoundError(Exception):
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.detail = f"Project {project_id} not found"


class SkillNotFoundError(Exception):
    def __init__(self, skill_id: str):
        self.skill_id = skill_id
        self.detail = f"Skill {skill_id} not found"


class ExperienceNotFoundError(Exception):
    def __init__(self, experience_id: str):
        self.experience_id = experience_id
        self.detail = f"Experience {experience_id} not found"