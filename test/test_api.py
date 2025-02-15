import os
from datetime import datetime
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
        ni_schools = [School(id=f"NI-{i}", update_timestamp=datetime(2025, 1, 1)) for i in range(10)]
        be_schools = [School(id="BE-1", update_timestamp=datetime(2024,12,24))]
        for school in ni_schools + be_schools:
            db.add(school)
        db.commit()

        response = client.get("/stats")

        assert response.status_code == 200
        assert response.json() == [
            {"state": "BE", "count": 1, "last_updated": "2024-12-24"},
            {"state": "NI", "count": 10, "last_updated": "2025-01-01"},
        ]


class TestFilterParams:
    def test_basic(self, client, db):
        # Arrange
        for school in [SchoolFactory(id="BY-1", legal_status="Privat", school_type="Grundschule"),
                       SchoolFactory(id="BY-2", legal_status="Privat", school_type="IGS"),
                       SchoolFactory(id="NI-1", legal_status="Staatlich", school_type="Gesamtschule"),
                       SchoolFactory(id="SN-3", legal_status="Staatlich", school_type="Grundschule"),
                       ]:
            db.add(school)
        db.commit()

        # Act
        # Act
        response = client.get("/filter_params")

        # Assert
        assert response.status_code == 200
        assert response.json() == {'legal_status': ['Staatlich', 'Privat'],
                                   'school_type': ['IGS', 'Grundschule', 'Gesamtschule'],
                                   'state': ['SN', 'NI', 'BY']
                                   }


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

    def test_filter_by_school_type(self, client, db):
        # Arrange
        for school in [SchoolFactory(school_type="Gymnasium"),
                       SchoolFactory(school_type="IGS"),
                       SchoolFactory(school_type="Grundschule")]:
            db.add(school)
        db.commit()

        # Act
        response = client.get("/schools?school_type=Gymnasium&school_type=IGS")

        # Assert
        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_filter_by_legal_status(self, client, db):
        # Arrange
        for school in [SchoolFactory(legal_status="Privat"),
                       SchoolFactory(legal_status="Staatlich"),
                       SchoolFactory(legal_status="Kirchlich")]:
            db.add(school)
        db.commit()

        # Act
        response = client.get("/schools?legal_status=Staatlich")

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

    def test_schools_ordered_by_distance(self, client, db):
        # Arrange
        for school in [
            SchoolFactory.create(location=None, id="BB-0"),
            SchoolFactory.create(location='SRID=4326;POINT(52.00  13.00)', id="BB-1"),
            SchoolFactory.create(location='SRID=4326;POINT(50.00  11.00)', id="BB-2"),
            SchoolFactory.create(location='SRID=4326;POINT(50.00  10.00)', id="BB-3")
        ]:
            db.add(school)
        db.commit()

        # Act?by_lat=52.00&by_lon=9.99&limit=1"t
        response = client.get("/schools?by_lat=52.00&by_lon=9.99&limit=1")

        # Assert
        assert response.status_code == 200
        schools = response.json()
        assert len(schools) == 1
        assert schools[0]['id'] == "BB-3"

    around_queries = [
        ("?by_lat=52", 400),
        ("?by_lon=10", 400),
        ("?by_lon=10&by_lat=52", 200),
    ]
    @pytest.mark.parametrize("query_params,status_code", around_queries)
    def test_around_param_validation(self, client, db, query_params, status_code):
        # Act
        response = client.get(f"/schools{query_params}")

        # Assert
        assert response.status_code == status_code


    bounding_box_queries = [
        ("?bb_top=52", 400),
        ("?bb_top=41&bb_bottom=10", 400),
        ("?bb_top=41&bb_bottom=10&bb_left=10", 400),
        ("?bb_top=41&bb_bottom=10&bb_left=10&bb_right=11", 200),
    ]
    @pytest.mark.parametrize("query_params,status_code", bounding_box_queries)
    def test_bounding_box_param_validation(self, client, db, query_params, status_code):
        # Act
        response = client.get(f"/schools{query_params}")

        # Assert
        assert response.status_code == status_code

    def test_schools_by_bounding_box(self, client, db):
        # Arrange
        for school in [
            SchoolFactory.create(location=None),
            SchoolFactory.create(location='SRID=4326;POINT(13.00 52.00)'),
            SchoolFactory.create(location='SRID=4326;POINT(11.00 51.00)'),
            SchoolFactory.create(location='SRID=4326;POINT(11.00 50.00)'),
            SchoolFactory.create(location='SRID=4326;POINT(09.00 50.00)')
        ]:
            db.add(school)
        db.commit()

        # Act
        response = client.get("/schools?bb_top=51.00&bb_bottom=49&bb_left=10&bb_right=12")

        # Assert
        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_schools_by_update_date(self, client, db):
        # Arrange
        for school in [
            SchoolFactory.create(update_timestamp=datetime(2024, 1, 1)),
            SchoolFactory.create(update_timestamp=datetime(2022, 1, 1)),
        ]:
            db.add(school)
        db.commit()

        # Act
        response = client.get("/schools?update_timestamp=2023-01-01")

        # Assert
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_schools_by_name(self, client, db):
        # Arrange
        for school in [
            SchoolFactory.create(name='Schule am kleinen Deich'),
            SchoolFactory.create(name='Schule an der Dorfstraßse'),
        ]:
            db.add(school)
        db.commit()

        # Act
        unfiltered_response = client.get("/schools")
        deich_response = client.get("/schools?name=deich")
        no_match_response = client.get("/schools?name=nicht%20da")

        # Assert
        assert unfiltered_response.status_code == 200
        assert deich_response.status_code == 200
        assert no_match_response.status_code == 200

        assert len(unfiltered_response.json()) == 2
        assert len(deich_response.json()) == 1
        assert len(no_match_response.json()) == 0

    def test_get_single_no_result(self, client, db):
        # Arrange
        self.__setup_schools(db)

        # Act
        response = client.get("/schools/NI-12345")

        # Assert
        assert response.status_code == 404

