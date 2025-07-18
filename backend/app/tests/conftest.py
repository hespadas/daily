from fastapi.testclient import TestClient
import pytest
import pytest_asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.security.password_utils import get_password_hash
from app.db.db import get_session
from app.main import app
from app.models.user import registry
from testcontainers.postgres import PostgresContainer

from app.tests.experiences.experience_factory import ExperienceFactory
from app.tests.projects.project_factory import ProjectFactory
from app.tests.users.user_factory import UserFactory


@pytest.fixture(scope="session")
def engine():
    with PostgresContainer() as postgres:
        _engine = create_engine(
            postgres.get_connection_url(),
        )
        with _engine.begin():
            yield _engine


@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def session(engine):
    registry.metadata.create_all(engine)

    with Session(engine) as session:
        yield session
        session.rollback()
    registry.metadata.drop_all(engine)


@pytest_asyncio.fixture
async def user(session):
    pwd = "testpassword"
    user = UserFactory(password=get_password_hash(pwd))
    session.add(user)
    session.commit()
    session.refresh(user)
    user.clean_password = pwd
    return user


@pytest_asyncio.fixture
async def another_user(session):
    another_user = UserFactory()
    session.add(another_user)
    session.commit()
    session.refresh(another_user)
    return another_user


@pytest_asyncio.fixture
async def experience(session):
    experience = ExperienceFactory()
    session.add(experience)
    session.commit()
    session.refresh(experience)
    return experience


@pytest_asyncio.fixture
async def project(session, user):
    project = ProjectFactory(user_id=user.id)
    session.add(project)
    session.commit()
    session.refresh(project)
    return project


@pytest.fixture()
def token(client, user):
    response = client.post(
        "/api/access_token",
        data={"username": user.username, "password": user.clean_password},
    )
    return response.json()["access_token"]
