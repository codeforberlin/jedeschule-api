import os
from typing import Iterator, Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.main import app, get_db
from app.database import Base
from app.models import School
from test.factory import SchoolFactory

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


@pytest.fixture(scope="function")
def db() -> Generator:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    yield TestingSessionLocal()


@pytest.fixture(scope="module")
def client() -> Generator:
    with TestClient(app) as c:
        yield c


class TestStats:
    def test_stats(self, client, db):
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


class TestStates:
    def __setup_schools(self, db):
        ni_schools = [SchoolFactory(id=f'NI-{i}') for i in range(10)]
        other_schools = [SchoolFactory(id='BE-1'), SchoolFactory(id='HE-1')]
        for school in ni_schools + other_schools:
            db.add(school)
        db.commit()

    def test_returns_all(self, client, db):
        # Arrange
        self.__setup_schools(db)

        # Act
        response = client.get("/schools")

        # Assert
        assert response.status_code == 200
        assert len(response.json()) == 12

    def test_filter_by_state(self, client, db):
        # Arrange
        self.__setup_schools(db)

        # Act
        response = client.get("/schools?state=HE")

        # Assert
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_filter_by_state_validates_state(self, client, db):
        # Arrange
        self.__setup_schools(db)

        # Act
        response = client.get("/schools?state=XX")

        # Assert
        assert response.status_code == 422
