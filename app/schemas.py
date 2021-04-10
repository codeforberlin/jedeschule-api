from __future__ import annotations

from enum import Enum
from typing import Optional

from geoalchemy2.shape import to_shape
from pydantic import BaseModel

from app import models


class State(Enum):
    BW = 'BW'
    BY = 'BY'
    BE = 'BE'
    BB = 'BB'
    HB = 'HB'
    HH = 'HH'
    HE = 'HE'
    MV = 'MV'
    NI = 'NI'
    NW = 'NW'
    RP = 'RP'
    SL = 'SL'
    SN = 'SN'
    ST = 'ST'
    SH = 'SH'
    TH = 'TH'


class School(BaseModel):
    id: str
    name: str
    address: str
    address2: Optional[str]
    city: Optional[str]
    director: Optional[str]
    email: Optional[str]
    fax: Optional[str]
    latitude: Optional[float]
    legal_status: Optional[str]
    longitude: Optional[float]
    phone: Optional[str]
    provider: Optional[str]
    school_type: Optional[str]
    website: Optional[str]
    zip: Optional[str]
    raw: Optional[dict]

    class Config:
        orm_mode = True

    @staticmethod
    def from_db(db_entry: models.School) -> School:
        if not db_entry.location:
            return School.from_orm(db_entry)
        shape = to_shape(db_entry.location)
        school = School.from_orm(db_entry)
        school.latitude = shape.x
        school.longitude = shape.y
        return school


class Statistic(BaseModel):
    state: str
    count: int

    class Config:
        schema_extra = {
            "example": [{
                "name": "BE",
                "count": 10,
            },
                {"name": "ND",
                 "count": 12}
            ]
        }
