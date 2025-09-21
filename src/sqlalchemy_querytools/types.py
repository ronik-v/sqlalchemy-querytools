from enum import StrEnum, ReprEnum

from sqlalchemy.orm import InstrumentedAttribute

QueryToolType = ReprEnum
TableFields = dict[str, InstrumentedAttribute]


class SortType(StrEnum):
    ASC = "ASC"
    DESC = "DESC"


class SearchType(StrEnum):
    ALL_FIELDS = "ALL_FIELDS"
    DATE_FIELDS = "DATE_FIELDS"
