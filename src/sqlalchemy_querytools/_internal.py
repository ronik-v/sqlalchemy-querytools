from abc import ABC, abstractmethod

from sqlalchemy import Select

from .types import QueryToolType, TableFields


class _QueryToolBuilderAbstract(ABC):
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
    def _use_extension(self) -> Select:
        raise NotImplemented("extension method is not realised")
