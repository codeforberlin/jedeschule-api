from typing import Optional

from pydantic import BaseModel


class School(BaseModel):
    id: str
    name: str
    address: str
    address2: Optional[str]
    zip : Optional[str]
    city : Optional[str]
    website: Optional[str]
    email: Optional[str]
    school_type: Optional[str]
    legal_status: Optional[str]
    provider: Optional[str]
    fax: Optional[str]
    phone: Optional[str]
    director: Optional[str]
    raw: dict

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
