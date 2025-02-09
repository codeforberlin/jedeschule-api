from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional, List

from geoalchemy2.shape import to_shape
from pydantic import ConfigDict, BaseModel

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
    address2: Optional[str] = None
    city: Optional[str] = None
    director: Optional[str] = None
    email: Optional[str] = None
    fax: Optional[str] = None
    latitude: Optional[float] = None
    legal_status: Optional[str] = None
    longitude: Optional[float] = None
    phone: Optional[str] = None
    provider: Optional[str] = None
    school_type: Optional[str] = None
    website: Optional[str] = None
    zip: Optional[str] = None
    raw: Optional[dict] = None
    update_timestamp: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

    @staticmethod
    def from_db(db_entry: models.School) -> School:
        if not db_entry.location:
            return School.model_validate(db_entry)
        shape = to_shape(db_entry.location)
        school = School.model_validate(db_entry)
        school.latitude = shape.x
        school.longitude = shape.y
        return school


class Statistic(BaseModel):
    state: State
    count: int
    last_updated: str
    model_config = ConfigDict(json_schema_extra={
        "example": [{
            "name": "BE",
            "count": 10,
            "last_updated": "2025-01-01"
        },
            {"name": "ND",
             "count": 12,
             "last_updated": "2025-01-01"
             }
        ]
    })


class Params(BaseModel):
    state: List[State]
    school_type: List[str]
    legal_status: List[str]
