try:
    from typing import override

except ImportError:
    from typing_extensions import override

from datetime import datetime, date

from sqlalchemy import (
    Select,
    BinaryExpression,
    ColumnElement,
    String,
    Text,
    Enum,
    DateTime,
    Date,
    cast,
    Cast,
    or_,
)

from ._internal import _QueryToolBuilderAbstract
from .types import SearchType, TableFields

Filters = list[BinaryExpression[bool] | ColumnElement[bool]]


class SearchQuery(_QueryToolBuilderAbstract):
    def __init__(
        self,
        stmt: Select,
        query_tool_type: SearchType,
        table_fields_relation: TableFields,
        search_value: str,
    ):
        super().__init__(stmt, query_tool_type, table_fields_relation)

        self._search_value = (search_value or "").strip()

    @override
    def build(self) -> Select:
        """Assembling a query with conditions"""
        search_query_filters: Filters = self._use_extension()
        if search_query_filters:
            self._stmt = self._stmt.where(or_(*search_query_filters))

        return self._stmt

    @override
    def _use_extension(self) -> Filters:
        """
        Search conditions by type
        When searching across all fields, it uses everything that falls within the field's select field
        """
        search_filters: Filters = []

        match self._query_tool_type:
            case SearchType.ALL_FIELDS:

                for str_field, orm_field in self._table_fields_relation.items():
                    if not isinstance(orm_field.type, (String, Text, Enum)):
                        orm_field = cast(orm_field, String)

                    search_filters.append(orm_field.ilike(f"%{self._search_value}%"))

            case SearchType.DATE_FIELDS:
                date_value: date = datetime.fromisoformat(self._search_value).date()
                date_fields: list[Cast[date]] = [
                    cast(_orm_field, Date)
                    for _, _orm_field in self._table_fields_relation.keys()
                    if isinstance(_orm_field.type, (DateTime, Date))
                ]

                for _date_field in date_fields:
                    search_filters.append(_date_field == date_value)

            case _:
                raise TypeError("Uncorrected search type")

        return search_filters
