from typing import List

from sqlalchemy.orm import Session

from . import models
from .schemas import School


def get_school(db: Session, school_id: str) -> School:
    school = db \
        .query(models.School) \
        .filter(models.School.id == school_id) \
        .first()
    return School.from_db(school)


def get_schools(db: Session, skip: int = 0, limit: int = 100, filter_params=None) -> List[School]:
    query = db.query(models.School)
    if filter_params:
        if 'state' in filter_params:
            names = [state.name for state in filter_params['state']]
            query = query.filter(models.School.state.in_(names))
        if 'school_type' in filter_params:
            query = query.filter(models.School.school_type.in_(filter_params['school_type']))
    return [School.from_db(school) for school in query.offset(skip).limit(limit).all()]


def get_stats(db: Session):
    response = db.execute("""select substring(id, 1, 2) as state, count(*) as count
from schools
group by state
order by state;""")
    return list(response)
