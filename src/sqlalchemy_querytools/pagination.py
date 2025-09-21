from sqlalchemy import Select


class PaginationQuery:
    def __init__(self, stmt: Select, offset: int, limit: int):
        self._stmt = stmt
        self._offset = offset
        self._limit = limit

    def build(self) -> Select:
        return self._stmt.limit(self._limit).offset(self._offset)
