import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model import Base, SignalTable
from api import app, get_db

DATABASE_URL = "sqlite:///./test.db"  # استفاده از SQLite برای تست

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def setup_database():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    db.add(SignalTable(cur_title="Bitcoin", channel_id=1, entry_zone="40000-41000", leverage="10x", created_date="2023-01-01"))
    db.add(SignalTable(cur_title="Ethereum", channel_id=2, entry_zone="2500-2600", leverage="5x", created_date="2023-01-02"))
    db.commit()
    yield
    db.close()
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)

def test_search_signals(setup_database):
    response = client.get("/signals/?cur_title=bit")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["cur_title"] == "Bitcoin"

def test_search_signals_case_insensitive(setup_database):
    response = client.get("/signals/?cur_title=BIT")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["cur_title"] == "Bitcoin"
