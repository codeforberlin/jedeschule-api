from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware


from . import crud, schemas
from .database import SessionLocal
from .schemas import State

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@app.get("/schools/", response_model=List[schemas.School] , response_model_exclude_none=True)
def read_schools(skip: int = 0,
                 limit: int = 100,
                 state: Optional[State] = None,
                 include_raw: bool = False,
                 db: Session = Depends(get_db)):
    filter_params = {}
    if state:
        filter_params['state'] = state
    schools = crud.get_schools(db, skip=skip, limit=limit, filter_params=filter_params)
    if include_raw:
        return schools
    return [school.dict(exclude={'raw'}) for school in schools]


@app.get("/schools/{school_id}", response_model=schemas.School, response_model_exclude_none=True)
def read_school(school_id: str, include_raw: bool = False, db: Session = Depends(get_db)):
    db_school = crud.get_school(db, school_id=school_id)
    if db_school is None:
        raise HTTPException(status_code=404, detail="School not found")
    if include_raw:
        return db_school
    return db_school.dict(exclude={'raw'})


@app.get("/stats", response_model=List[schemas.Statistic])
def get_stats(db: Session = Depends(get_db)):
    """Returns the total count of schools grouped by state.
       States are represented using their ISO-3166-2:DE codes """
    return crud.get_stats(db)
