from typing import override

from sqlalchemy import Select

from ._internal import _QueryToolBuilderAbstract
from .types import SearchType, TableFields


class SearchQuery(_QueryToolBuilderAbstract):
    def __init__(
        self,
        stmt: Select,
        query_tool_type: SearchType,
        table_fields_relation: TableFields,
        search_value: str,
    ):
        super().__init__(stmt, query_tool_type, table_fields_relation)

        self._search_value = search_value

    @override
    def build(self) -> Select:
        """TODO"""

    @override
    def _use_extension(self) -> Select:
        """TODO"""
