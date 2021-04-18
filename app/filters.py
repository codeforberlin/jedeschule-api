from typing import List

from sqlalchemy import func, asc
from sqlalchemy.orm import Query

from app import models


class Filter:
    supported_keys: List[str] = []

    def __init__(self, key, values):
        self.key = key
        self.values = values

    @classmethod
    def handles(cls, key: str) -> bool:
        return key in cls.supported_keys

    @staticmethod
    def apply(query: Query) -> Query:
        pass


class StateFilter(Filter):
    supported_keys = ['state']

    def apply(self, query):
        names = [state.name for state in self.values]
        return query.filter(models.School.state.in_(names))


class BasicFilter(Filter):
    supported_keys = ['school_type', 'legal_status']

    def apply(self, query):
        column_to_filter = getattr(models.School, self.key)
        return query.filter(column_to_filter.in_(self.values))


class BoundingBoxFilter(Filter):
    supported_keys = ['bounding_box']

    def apply(self, query):
        return query.filter(
            models.School.location.intersects(
                func.ST_MakeEnvelope(
                    self.values['left'], self.values['top'],
                    self.values['right'], self.values['bottom']
                )
            )
        )


class LatLonSorter(Filter):
    supported_keys = ['around']

    def apply(self, query):
        point = f"SRID=4326;POINT({self.values['lat']} {self.values['lon']})"
        return query.order_by(asc(func.ST_Distance(models.School.location, point)))


class SchoolFilter:
    filter_classes = [StateFilter, BasicFilter, LatLonSorter, BoundingBoxFilter]

    def __init__(self, params):
        self.used_filters = []
        for (key, values) in params.items():
            if values is None:
                continue
            try:
                filter_class = next((fc for fc in self.filter_classes if fc.handles(key)))
                self.used_filters.append(filter_class(key, values))
            except StopIteration:
                print(f'Tried to filter for unknown column {key}')

    def apply(self, query):
        for filter in self.used_filters:
            query = filter.apply(query)
        return query
