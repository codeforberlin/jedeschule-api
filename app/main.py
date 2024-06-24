from datetime import datetime, date
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.openapi.utils import get_openapi
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


@app.get("/schools/", response_model=List[schemas.School], response_model_exclude_none=True)
def read_schools(skip: int = 0,
                 limit: int = 100,
                 state: Optional[List[State]] = Query(None),
                 school_type: Optional[List[str]] = Query(None),
                 legal_status: Optional[List[str]] = Query(None),
                 name: Optional[str] = Query(None,
                                             description="Allows searching for names of schools."
                                                         "Searches for case-insensitive substrings."),
                 by_lat: Optional[float] = Query(None,
                                                 description="Allows ordering result by distance from a geographical point."
                                                             "Must be used in combination with `by_lon`"
                                                             "Value must be in CRS EPSG:4326"
                                                 ),
                 by_lon: Optional[float] = Query(None,
                                                 description="Allows ordering result by distance from a geographical point. "
                                                             "Must be used in combination with `by_lat`"
                                                             "Value must be in CRS EPSG:4326"
                                                 ),
                 bb_top: Optional[float] = Query(None,
                                                 description="Allows filtering results by bounding box."
                                                             "Must be used in combination with `bb_bottom`, `bb_left` and `bb_right`"
                                                             "Value must be in CRS EPSG:4326"
                                                 ),
                 bb_bottom: Optional[float] = Query(None,
                                                    description="Allows filtering results by bounding box. See `bb_top` for details."),
                 bb_left: Optional[float] = Query(None,
                                                  description="Allows filtering results by bounding box. See `bb_top` for details."),
                 bb_right: Optional[float] = Query(None,
                                                   description="Allows filtering results by bounding box. See `bb_top` for details."),
                 update_timestamp: Optional[date] = Query(None,
                                                   description="Allows filtering to only results scraped after the given date."),
                 include_raw: bool = False,
                 db: Session = Depends(get_db)):
    filter_params = {
        "state": state,
        "school_type": school_type,
        "legal_status": legal_status,
        "update_timestamp": update_timestamp,
        "name": name,
    }
    if by_lat or by_lon:
        if not (by_lon and by_lat):
            raise HTTPException(status_code=400, detail="To order by point, you need to provide by_lon and by_lat.")
        filter_params["around"] = {"lat": by_lat, "lon": by_lon}
    bounding_box = {
        "top": bb_top,
        "bottom": bb_bottom,
        "left": bb_left,
        "right": bb_right
    }
    bounding_box_count = len([value for value in bounding_box.values() if value is not None])
    if bounding_box_count != 0:
        if bounding_box_count != 4:
            raise HTTPException(status_code=400, detail="To filter by bounding box, you need to provide all `bb_` values.")
        filter_params["bounding_box"] = bounding_box
    schools = crud.get_schools(db, skip=skip, limit=limit, filter_params=filter_params)
    if include_raw:
        return schools
    return [school.model_dump(exclude={'raw'}) for school in schools]


@app.get("/schools/{school_id}", response_model=schemas.School, response_model_exclude_none=True)
def read_school(school_id: str, include_raw: bool = False, db: Session = Depends(get_db)):
    db_school = crud.get_school(db, school_id=school_id)
    if db_school is None:
        raise HTTPException(status_code=404, detail="School not found")
    if include_raw:
        return db_school
    return db_school.model_dump(exclude={'raw'})


@app.get("/stats", response_model=List[schemas.Statistic])
def get_stats(db: Session = Depends(get_db)):
    """Returns the total count of schools grouped by state.
       States are represented using their ISO-3166-2:DE codes """
    return crud.get_stats(db)


@app.get("/filter_params", response_model=schemas.Params)
def get_filter_params(db: Session = Depends(get_db)):
    """Returns distinct values for keys that can be used as
       filters.py in the `/schools/` endpoint"""
    return crud.get_params(db)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="jedeschule-api",
        version="0.1.0",
        description="This API allows you to query information about German schools.\n\n"
                    "The schools are scraped as part of the [jedeschule.de](https://jedeschule.de) project."
                    "You can find the source code for the [API](https://github.com/codeforberlin/jedeschule-api) and "
                    "the [scrapers](https://github.com/datenschule/jedeschule-scraper) on Github. \n\n"
                    "For more information about the available endpoints, check the documentation below.",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
