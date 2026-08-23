import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
import os
import sys

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["TESTING"] = "1"
os.environ["SECRET_KEY"] = "testsecretkey"

from main import app
from database import Base, get_db
import models

# Use in-memory SQLite to avoid disk I/O errors in Docker container mapping
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    
    # Create default organization for tests
    org = models.Organization(id=1, name="Test Org")
    session.add(org)
    session.commit()
    
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        yield db_session
            
    app.dependency_overrides[get_db] = override_get_db
    
    from auth import get_current_user
    app.dependency_overrides[get_current_user] = lambda: {"id": 1, "email": "admin@ironsight.ai", "role": "admin", "organization_id": 1}
    
    from auth import create_access_token
    token = create_access_token({"id": 1, "email": "admin@ironsight.ai", "role": "admin", "organization_id": 1})
    
    with TestClient(app, headers={"Authorization": f"Bearer {token}"}) as c:
        yield c
    app.dependency_overrides.clear()

