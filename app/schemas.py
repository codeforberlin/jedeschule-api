from typing import Optional

from pydantic import BaseModel


class School(BaseModel):
    id: str
    name: str
    address: str
    website: Optional[str]
    email: Optional[str]
    school_type: Optional[str]
    legal_status: Optional[str]
    provider: Optional[str]
    fax: Optional[str]
    phone: Optional[str]
    raw: dict

    class Config:
        orm_mode = True

