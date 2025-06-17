import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool
from typing import Generator, Dict

from app.main import app
from app.db.session import get_db_session
from app.core.config import get_settings
from app.models.user import User
from app.services.user import user_service
from app.core.security import create_access_token

settings = get_settings()

# Test database URL
TEST_DATABASE_URL = "sqlite://"

@pytest.fixture(scope="session")
def test_engine():
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    yield engine

@pytest.fixture(scope="function")
def test_db(test_engine) -> Generator[Session, None, None]:
    connection = test_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(test_db) -> Generator[TestClient, None, None]:
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db_session] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def test_user(test_db) -> User:
    user = User(
        email="test@example.com",
        name="Test User",
        role="user",
        password_hash="hashed_password",
        is_active=True
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user

@pytest.fixture(scope="function")
def test_admin(test_db) -> User:
    admin = User(
        email="admin@example.com",
        name="Admin User",
        role="admin",
        password_hash="hashed_password",
        is_active=True
    )
    test_db.add(admin)
    test_db.commit()
    test_db.refresh(admin)
    return admin

@pytest.fixture(scope="function")
def user_token_headers(test_user) -> Dict[str, str]:
    access_token = create_access_token(test_user.id)
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture(scope="function")
def admin_token_headers(test_admin) -> Dict[str, str]:
    access_token = create_access_token(test_admin.id)
    return {"Authorization": f"Bearer {access_token}"} 