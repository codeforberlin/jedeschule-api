from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy.sql import text

from . import models
from .filters import SchoolFilter
from .schemas import School


def get_school(db: Session, school_id: str) -> Optional[School]:
    school = db \
        .query(models.School) \
        .filter(models.School.id == school_id) \
        .first()
    if school:
        return School.from_db(school)
    return None



def get_schools(db: Session, skip: int = 0, limit: int = 100, filter_params=None) -> List[School]:
    query = db.query(models.School)
    school_filter = SchoolFilter(filter_params)
    query = school_filter.apply(query)
    return [School.from_db(school) for school in query.offset(skip).limit(limit).all()]


def get_stats(db: Session):
    response = db.execute(text("""select
        substring(id, 1, 2) as state,
        count(*) as count,
        max(update_timestamp)::date as last_updated
from schools
group by state
order by state;"""))
    return [row._mapping for row in response]


def _get_states(db: Session):
    return [state for state, in db.execute(text("select distinct(substring(id, 1, 2)) from schools;"))]


def _get_school_types(db: Session):
    return [school_type for school_type, in
            db.execute(text("select distinct(school_type) from schools where school_type is not null;"))
            ]


def _get_legal_status(db: Session):
    return [school_type for school_type, in
            db.execute(text("select distinct(legal_status) from schools where legal_status is not null;"))
            ]


def get_params(db):
    return {
        "state": _get_states(db),
        "school_type": _get_school_types(db),
        "legal_status": _get_legal_status(db)
    }
