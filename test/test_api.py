import os
from typing import Iterator, Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.main import app, get_db
from app.database import Base
from app.models import School

SQLALCHEMY_DATABASE_URL = ""

engine = create_engine(
    os.environ.get("DATABASE_URL_TEST")
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db() -> Iterator[Session]:
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session")
def db() -> Generator:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    yield TestingSessionLocal()


@pytest.fixture(scope="module")
def client() -> Generator:
    with TestClient(app) as c:
        yield c


def test_read_main(client, db):
    ni_schools = [School(id=f'NI-{i}') for i in range(10)]
    be_schools = [School(id='BE-1')]
    for school in ni_schools + be_schools:
        db.add(school)
    db.commit()

    response = client.get("/stats")

    assert response.status_code == 200
    assert response.json() == [{
        "state": "BE",
        "count": 1
    }, {
        "state": "NI",
        "count": 10
    }]
