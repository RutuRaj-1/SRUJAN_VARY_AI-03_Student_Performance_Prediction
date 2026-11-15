import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.models.institution import Institution

# Shared in-memory test database for test suite
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        inst1 = Institution(
            id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
            name="Alpha Engineering College",
            institution_code="ALPHA-TEST",
            institution_type="COLLEGE",
            city="Bengaluru",
            state="Karnataka",
        )
        inst2 = Institution(
            id=uuid.UUID("22222222-2222-2222-2222-222222222222"),
            name="Beta Institute of Tech",
            institution_code="BETA-TEST",
            institution_type="UNIVERSITY",
            city="Hyderabad",
            state="Telangana",
        )
        inst3 = Institution(
            id=uuid.UUID("33333333-3333-3333-3333-333333333333"),
            name="Gamma Global Institute",
            institution_code="GAMMA-TEST",
            institution_type="INSTITUTE",
            city="Pune",
            state="Maharashtra",
        )
        session.add_all([inst1, inst2, inst3])
        session.commit()
    finally:
        session.close()


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="module")
def client():
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.pop(get_db, None)
