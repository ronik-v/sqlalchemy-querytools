from typing import override

from sqlalchemy import Select

from ._internal import _QueryToolBuilderAbstract
from .types import SortType, TableFields


class SortQuery(_QueryToolBuilderAbstract):
    def __init__(
        self,
        stmt: Select,
        query_tool_type: SortType,
        table_fields_relation: TableFields,
        sort_field: str,
    ):
        super().__init__(stmt, query_tool_type, table_fields_relation)

        self._sort_field = sort_field

    @override
    def build(self) -> Select:
        """TODO"""

    @override
    def _use_extension(self) -> Select:
        """TODO"""
