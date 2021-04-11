from typing import List

from sqlalchemy.orm import Session

from . import models
from .filters import SchoolFilter
from .schemas import School


def get_school(db: Session, school_id: str) -> School:
    school = db \
        .query(models.School) \
        .filter(models.School.id == school_id) \
        .first()
    return School.from_db(school)


def get_schools(db: Session, skip: int = 0, limit: int = 100, filter_params=None) -> List[School]:
    query = db.query(models.School)
    school_filter = SchoolFilter(filter_params)
    query = school_filter.apply(query)
    return [School.from_db(school) for school in query.offset(skip).limit(limit).all()]


def get_stats(db: Session):
    response = db.execute("""select substring(id, 1, 2) as state, count(*) as count
from schools
group by state
order by state;""")
    return list(response)


def _get_states(db: Session):
    return [state for state, in db.execute("select distinct(substring(id, 1, 2)) from schools;")]


def _get_school_types(db: Session):
    return [school_type for school_type, in
            db.execute("select distinct(school_type) from schools where school_type is not null;")
            ]


def _get_legal_status(db: Session):
    return [school_type for school_type, in
            db.execute("select distinct(legal_status) from schools where legal_status is not null;")
            ]


def get_params(db):
    return {
        "state": _get_states(db),
        "school_type": _get_school_types(db),
        "legal_status": _get_legal_status(db)
    }
