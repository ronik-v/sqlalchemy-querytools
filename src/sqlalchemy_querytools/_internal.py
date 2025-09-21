from abc import ABC, abstractmethod
from typing import Any

from sqlalchemy import Select

from .types import QueryToolType, TableFields


class _QueryToolBuilderAbstract(ABC):
    """

    A base class for describing specific modifications to select queries with sqlalchemy.
    QueryToolType - an enum for defining the query type in a specific implementation.
    TableFields - a dictionary of the form string (database field name / JSON field)
    -> ORM table field. *Sometimes you can insert sqlalchemy.text with the field name.
    """

    def __init__(
        self,
        stmt: Select,
        query_tool_type: QueryToolType,
        table_fields_relation: TableFields,
    ):
        self._stmt = stmt
        self._query_tool_type = query_tool_type
        self._table_fields_relation = table_fields_relation

    @abstractmethod
    def build(self) -> Select:
        raise NotImplemented("build method is not realised")

    @abstractmethod
    def _use_extension(self) -> Any:
        raise NotImplemented("extension method is not realised")
