from geoalchemy2 import Geometry
from sqlalchemy import Column, String, JSON

from .database import Base


class School(Base):
    __tablename__ = 'schools'
    id = Column(String, primary_key=True)
    name = Column(String)
    address = Column(String)
    address2 = Column(String)
    zip = Column(String)
    city = Column(String)
    website = Column(String)
    email = Column(String)
    school_type = Column(String)
    legal_status = Column(String)
    provider = Column(String)
    fax = Column(String)
    phone = Column(String)
    director = Column(String)
    raw = Column(JSON)
    location = Column(Geometry('POINT'))

