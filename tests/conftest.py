import pytest
import uuid
from fastapi.testclient import TestClient
from assistant.main import app
from sqlalchemy import create_engine, true
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import StaticPool
from assistant.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread" : False},
    poolclass = StaticPool
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client() ->TestClient:
    return TestClient(app)


@pytest.fixture()
def auth_headers(client):
    user_data = {
        "email" : f"test_{uuid.uuid4().hex[:8]}@gmail.com",
        "name" : "sayMyName",
        "password" : "strongPassword"
    }

    user_register = client.post("/auth/register", json=user_data)

    assert user_register.status_code == 201

    login_data = {
        "username" : user_data["email"],
        "password" : user_data["password"]
    }

    response = client.post("/auth/login", data=login_data)
    token = response.json()["access_token"]

    return {"Authorization" : f"Bearer {token}"}

@pytest.fixture()
def db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()