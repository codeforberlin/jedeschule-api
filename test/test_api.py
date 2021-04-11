import os
from typing import Iterator, Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.main import app, get_db
from app.database import Base
from app.models import School
from test.factory import SchoolFactory, get_full_school

engine = create_engine(os.environ.get("DATABASE_URL_TEST"))
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
        ni_schools = [School(id=f"NI-{i}") for i in range(10)]
        be_schools = [School(id="BE-1")]
        for school in ni_schools + be_schools:
            db.add(school)
        db.commit()

        response = client.get("/stats")

        assert response.status_code == 200
        assert response.json() == [
            {"state": "BE", "count": 1},
            {"state": "NI", "count": 10},
        ]


class TestStates:
    def __setup_schools(self, db):
        ni_schools = [SchoolFactory(id=f"NI-{i}") for i in range(5)]
        by_schools = [SchoolFactory(id=f"BY-{i}") for i in range(5)]
        other_schools = [get_full_school(), SchoolFactory(id="HE-1")]
        for school in ni_schools + by_schools + other_schools:
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

    def test_filter_by_multiple_states(self, client, db):
        # Arrange
        self.__setup_schools(db)

        # Act
        response = client.get("/schools?state=HE&state=BY")

        # Assert
        assert response.status_code == 200
        assert len(response.json()) == 6

    def test_filter_by_state_validates_state(self, client, db):
        # Arrange
        self.__setup_schools(db)

        # Act
        response = client.get("/schools?state=XX")

        # Assert
        assert response.status_code == 422

    def test_schools_json_default_without_raw(self, client, db):
        # Arrange
        self.__setup_schools(db)

        # Act
        response = client.get("/schools?state=NW")

        # Assert
        assert response.json() == [
            {
                "id": "NW-112586",
                "name": "Städt. Gem. Grundschule - Primarstufe -",
                "address": "Pfälzer Str. 30-34",
                "city": "Köln",
                "email": "112586@schule.nrw.de",
                "fax": "0221355007718",
                "legal_status": "in öffentlicher Trägerschaft",
                "phone": "022135500770",
                "provider": "Stadt Köln",
                "school_type": "Grundschule",
                "website": "http://www.ggs-pfaelzer-strasse-koeln.de",
                "zip": "50677",
            }
        ]

    def test_schools_json_with_raw(self, client, db):
        # Arrange
        self.__setup_schools(db)

        # Act
        response = client.get("/schools?state=NW&include_raw=true")

        # Assert
        assert response.json() == [
            {
                "id": "NW-112586",
                "name": "Städt. Gem. Grundschule - Primarstufe -",
                "address": "Pfälzer Str. 30-34",
                "city": "Köln",
                "email": "112586@schule.nrw.de",
                "fax": "0221355007718",
                "legal_status": "in öffentlicher Trägerschaft",
                "phone": "022135500770",
                "provider": "Stadt Köln",
                "school_type": "Grundschule",
                "website": "http://www.ggs-pfaelzer-strasse-koeln.de",
                "zip": "50677",
                "raw": {
                    "Schulnummer": "112586",
                    "Schulform": "02",
                    "Schulbezeichnung_1": "Städt. Gem. Grundschule",
                    "Schulbezeichnung_2": "- Primarstufe -",
                    "Schulbezeichnung_3": "",
                    "Kurzbezeichnung": "Köln, GG Pfälzer Str.",
                    "PLZ": "50677",
                    "Ort": "Köln",
                    "Strasse": "Pfälzer Str. 30-34",
                    "Telefonvorwahl": "0221",
                    "Telefon": "35500770",
                    "Faxvorwahl": "0221",
                    "Fax": "355007718",
                    "E-Mail": "112586@schule.nrw.de",
                    "Homepage": "http://www.ggs-pfaelzer-strasse-koeln.de",
                    "Rechtsform": "1",
                    "Traegernummer": "10182",
                    "Gemeindeschluessel": "05315000",
                    "Schulbetriebsschluessel": "1",
                    "Schulbetriebsdatum": "01.08.1973",
                    "EPSG": "EPSG:25832",
                    "UTMRechtswert": "355389",
                    "UTMHochwert": "5643630",
                },
            }
        ]

    def test_schools_json_exposes_lat_and_lon(self, client, db):
        # Arrange
        school = SchoolFactory(
            id=f"NW-100010",
            location="SRID=4326;POINT(50.94217152830834 6.897017373118707)",
            name="Gymnasium Claudia Agrippina Privat schule als priv.Ersatzsch. d. Sek.I u.II im Aufbau d. CAPS Privatschu gGmbH",
            address="Stolberger Str. 112",
        )

        db.add(school)
        db.commit()

        # Act
        response = client.get("/schools/NW-100010")

        # Assert
        assert response.json() == {
            "id": "NW-100010",
            "name": "Gymnasium Claudia Agrippina Privat schule als priv.Ersatzsch. d. Sek.I u.II im Aufbau d. CAPS Privatschu gGmbH",
            "address": "Stolberger Str. 112",
            "latitude": 50.94217152830834,
            "longitude": 6.897017373118707,
        }
