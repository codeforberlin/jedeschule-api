import random

import factory

from app.models import School
from app.schemas import State


class SchoolFactory(factory.Factory):
    class Meta:
        model = School

    @staticmethod
    def _get_state(n):
        states = [state.name for state in State]
        return states[n % len(states)]

    id = factory.Sequence(lambda n: "{}-{}".format(SchoolFactory._get_state(n), n))
    name = factory.Sequence(lambda n: 'School %d' % n)
    address = factory.Faker('address')


def get_full_school():
    return School(
        id="NW-112586",
        name="Städt. Gem. Grundschule - Primarstufe -",
        address="Pfälzer Str. 30-34",
        city="Köln",
        email="112586@schule.nrw.de",
        fax="0221355007718",
        legal_status="in öffentlicher Trägerschaft",
        phone="022135500770",
        provider="Stadt Köln",
        school_type="Grundschule",
        website="http://www.ggs-pfaelzer-strasse-koeln.de",
        zip="50677",
        raw={
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
    )


