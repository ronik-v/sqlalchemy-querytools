try:
    from typing import override

except ImportError:
    from typing_extensions import override

from sqlalchemy import Select, asc, desc, UnaryExpression
from sqlalchemy.orm import InstrumentedAttribute

from ._internal import _QueryToolBuilderAbstract
from .types import SortType, TableFields


class SortQuery(_QueryToolBuilderAbstract):
    def __init__(
        self,
        stmt: Select,
        query_tool_type: SortType,
        table_fields_relation: TableFields,
        sort_field: str,
        null_last: bool = False,
    ):
        super().__init__(stmt, query_tool_type, table_fields_relation)

        self._sort_field = sort_field
        self._null_last = null_last

    @override
    def build(self) -> Select:
        """Assembling a query for sorting"""
        ordered_field: UnaryExpression = (
            self._use_extension().nullslast()
            if self._null_last
            else self._use_extension().nullsfirst()
        )

        return self._stmt.order_by(ordered_field)

    @override
    def _use_extension(self) -> UnaryExpression:
        """
        If a field (string value of a field in the database)
        is missing from the dictionary, a KeyError will occur
        """
        field: InstrumentedAttribute = self._table_fields_relation[self._sort_field]

        match self._query_tool_type:
            case SortType.ASC:
                return asc(field)

            case SortType.DESC:
                return desc(field)

            case _:
                raise TypeError("Uncorrected sort type")
