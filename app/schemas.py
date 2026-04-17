from __future__ import annotations

from datetime import datetime, date
from enum import Enum
from typing import Optional, List

from geoalchemy2.shape import to_shape
from pydantic import BaseModel, ConfigDict, Field

from sqlalchemy.inspection import inspect as sa_inspect

from app import models
from app.state_key import parse_state_key_column


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
    state_key: Optional[State] = Field(
        default=None,
        description=(
            "ISO 3166-2:DE subdivision code without the DE- prefix (same vocabulary as the `state` "
            "query filter). Stored in the database from the Land scraper that produced the row "
            "(same code used when composing `id`); identifies which JedeSchule feed produced the row "
            "(not coordinates). Aligns with pipeline-declared `state_key` for split-by-Land jobs. "
            "Omitted when unset or not a known code."
        ),
    )
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
        insp = sa_inspect(db_entry)
        cols = {c.key: getattr(db_entry, c.key) for c in insp.mapper.column_attrs}
        cols.pop("location", None)
        cols["state_key"] = parse_state_key_column(cols.get("state_key"))
        school = School.model_validate(cols)
        if db_entry.location:
            shape = to_shape(db_entry.location)
            school.latitude = shape.y
            school.longitude = shape.x
        return school


class Statistic(BaseModel):
    state: State
    count: int
    last_updated: date
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
