import pytest

from app.models.portfolio_embedding import PortfolioEmbedding
from app.repositories.project_repository import ProjectRepository
from app.repositories.skill_repository import SkillRepository
from app.schemas.project import ProjectCreate
from app.schemas.skill import SkillCreate
from app.services import portfolio_index

pytestmark = pytest.mark.integration

# A tiny fake embedding space: one dimension per topic keyword.
TOPICS = ["chatbot", "docker", "python"]


def fake_vector(text: str) -> list[float]:
    text = text.lower()
    return [1.0 if topic in text else 0.0 for topic in TOPICS] + [0.1]


@pytest.fixture(autouse=True)
def fake_embeddings(monkeypatch):
    async def embed(texts, task):
        return [fake_vector(t) for t in texts]

    monkeypatch.setattr(portfolio_index.gemini, "embed", embed)


async def test_search_returns_most_relevant_items_first(db):
    bot = await ProjectRepository().create(
        ProjectCreate(name="Portfolio chatbot", description="An ADK chatbot", tech_stack=["Gemini"])
    )
    docker = await SkillRepository().create(SkillCreate(name="Docker", level="Intermediate"))
    for doc in (bot, docker):
        await portfolio_index.index_document(doc)

    hits = await portfolio_index.search("Has she built a chatbot?", k=2)

    assert hits[0].source_type == "project"
    assert hits[0].source_id == str(bot.id)
    assert hits[0].score > hits[1].score


async def test_reindexing_an_item_replaces_its_embedding(db):
    repo = SkillRepository()
    skill = await repo.create(SkillCreate(name="Python", level="Beginner"))
    await portfolio_index.index_document(skill)
    updated = await repo.update(skill.id, SkillCreate(name="Python", level="Expert"))
    await portfolio_index.index_document(updated)

    chunks = await PortfolioEmbedding.find_all().to_list()
    assert len(chunks) == 1
    assert "Expert" in chunks[0].text


async def test_remove_and_reindex_all(db):
    skill = await SkillRepository().create(SkillCreate(name="Docker", level="Advanced"))
    project = await ProjectRepository().create(ProjectCreate(name="API", description="python", tech_stack=[]))
    await portfolio_index.index_document(skill)
    await portfolio_index.remove_document("skill", skill.id)
    assert await PortfolioEmbedding.count() == 0

    assert await portfolio_index.reindex_all() == 2
    assert {c.source_id for c in await PortfolioEmbedding.find_all().to_list()} == {skill.id, project.id}
