
from enum import Enum
from typing import Optional

from pydantic import BaseModel

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
    legal_status: Optional[str]
    phone: Optional[str]
    provider: Optional[str]
    school_type: Optional[str]
    website: Optional[str]
    zip: Optional[str]
    raw: Optional[dict]

    class Config:
        orm_mode = True


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
