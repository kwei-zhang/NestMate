from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.db import Base, get_db
from app.core.security import create_access_token
from app.deps import get_current_user
from app.main import app
from app.models import Listing, User


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def user(db_session) -> User:
    u = User(provider="google", provider_id="g1", email="u@example.com", display_name="U")
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)
    return u


@pytest.fixture
def auth_headers(user) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token(user.id)}"}


@pytest.fixture
def published_listing(db_session) -> Listing:
    listing = Listing(
        source="xhs",
        source_url="https://www.xiaohongshu.com/explore/abc",
        title="北约克求室友",
        raw_text="INFP女生 North York 求室友 预算1000 有猫 微信 abc123",
        status="published",
        intent="seeking",
        has_room=False,
        mbti="INFP",
        has_pets=True,
        budget_min=900,
        budget_max=1100,
        area="North York",
        contact_type="wechat",
        contact_value="abc123",
        published_at=datetime.now(UTC),
    )
    db_session.add(listing)
    db_session.commit()
    db_session.refresh(listing)
    return listing
