from sqlalchemy.orm import Session

from . import models


def get_school(db: Session, school_id: str):
    return db.query(models.School).filter(models.School.id == school_id).first()


def get_schools(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.School).offset(skip).limit(limit).all()


def get_stats(db: Session, skip: int = 0, limit: int = 100):
    response = db.execute("""select substring(id, 1, 2) as state, count(*) as count
from schools
group by state
order by state;""")
    return list(response)
