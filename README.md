# sqlalchemy-querytools

Lightweight helpers to build SQLAlchemy `SELECT` queries with common list-table features: **search**, **sort**, and *
*pagination**.  
Each tool accepts a `sqlalchemy.Select` and returns a modified `Select`. Designed to be composed — ideal for APIs, CRUD
endpoints and list pages.

**Version:** `0.1.0`  
**License:** MIT

---

## Table of contents

- [Purpose](#purpose)
- [Install](#install)
- [Quick example](#quick-example)
- [Public API](#public-api)
- [Behavior details](#behavior-details)
- [Examples](#examples)
    - [Search (ALL_FIELDS)](#search-all_fields)
    - [Search (DATE_FIELDS)](#search-date_fields)
    - [Sort (ASC / DESC) and null placement](#sort-asc--desc-and-null-placement)
    - [Pagination (limit / offset)](#pagination-limit--offset)
    - [Compose: search + sort + paginate](#compose-search--sort--paginate)
- [Tests](#tests)
- [Notes / gotchas](#notes--gotchas)
- [Contributing](#contributing)
- [License](#license)

---

## Purpose

`sqlalchemy-querytools` provides three small, composable builders that make it easy to add common list-table features to
SQLAlchemy queries:

- `SearchQuery` — builds `WHERE` clauses for text/date searching across model fields.
- `SortQuery` — builds `ORDER BY` with ASC/DESC and controls null placement.
- `PaginationQuery` — applies `LIMIT` and `OFFSET`.

Each builder returns a `sqlalchemy.Select` that you then execute with your session.

---

## Install

If published to PyPI:

```bash
pip install sqlalchemy-querytools
```

Or install locally:

```bash
pip install -e .
```

Requirements: SQLAlchemy (version compatible with your project). For running tests: `pytest`.

---

## Quick example

```python
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from sqlalchemy_querytools import SearchQuery, SortQuery, PaginationQuery
from sqlalchemy_querytools.types import SearchType, SortType

# assume engine, Session, and User model are already defined
session = Session()

table_fields = {
    "name": User.name,
    "email": User.email,
    "created_at": User.created_at,
}

stmt = select(User)

# search -> sort -> paginate
stmt = SearchQuery(stmt, SearchType.ALL_FIELDS, table_fields, "alice").build()
stmt = SortQuery(stmt, SortType.ASC, table_fields, "name", null_last=False).build()
stmt = PaginationQuery(stmt, offset=0, limit=20).build()

users = session.execute(stmt).scalars().all()
```

---

## Public API

Exports (from `__all__`):

- `SearchQuery(stmt: Select, query_tool_type: SearchType, table_fields_relation: TableFields, search_value: str)`
    - `.build() -> Select`
- `SortQuery(stmt: Select, query_tool_type: SortType, table_fields_relation: TableFields, sort_field: str, null_last: bool = False)`
    - `.build() -> Select`
- `PaginationQuery(stmt: Select, offset: int, limit: int)`
    - `.build() -> Select`
- `SearchType` — enum values: `ALL_FIELDS`, `DATE_FIELDS`
- `SortType` — enum values: `ASC`, `DESC`
- `TableFields` — `dict[str, InstrumentedAttribute]` (mapping names → SQLAlchemy attributes)

---

## Behavior details

**SearchQuery**

- `SearchType.ALL_FIELDS`
    - Builds `ilike('%value%')` for each mapped field.
    - If a mapped field is non-text, the implementation casts to `String` before applying `ilike`.
    - If `search_value` is empty or whitespace, no filters are added and the original `Select` is returned.
- `SearchType.DATE_FIELDS`
    - Expects `search_value` parseable via `datetime.fromisoformat` (e.g. `"2020-01-01"`), converts to `date` and
      compares equality against `Date`/`DateTime` fields.
    - Invalid date string → `ValueError` from `datetime.fromisoformat`.
- Unknown `SearchType` → `TypeError("Uncorrected search type")`.

**SortQuery**

- Looks up `sort_field` in `table_fields_relation`. Missing key → `KeyError`.
- `SortType.ASC` → `asc(field)`; `SortType.DESC` → `desc(field)`.
- `null_last=True` uses `.nullslast()`, otherwise `.nullsfirst()`.
- Unknown `SortType` → `TypeError("Uncorrected sort type")`.

**PaginationQuery**

- Applies `.limit(limit).offset(offset)` on the `Select`.

---

## Examples

### Search (ALL_FIELDS)

```python
from sqlalchemy_querytools import SearchQuery
from sqlalchemy_querytools.types import SearchType

stmt = select(User)
search = SearchQuery(stmt, SearchType.ALL_FIELDS, {"name": User.name, "email": User.email}, "ann")
result = session.execute(search.build()).scalars().all()
```

### Search (DATE_FIELDS)

```python
search = SearchQuery(select(User), SearchType.DATE_FIELDS, {"created_at": User.created_at}, "2020-01-01")
rows = session.execute(search.build()).scalars().all()
# Note: the date string must be ISO-like and parseable by datetime.fromisoformat
```

### Sort (ASC / DESC) and null placement

```python
from sqlalchemy_querytools import SortQuery
from sqlalchemy_querytools.types import SortType

# ascending, NULLs first (default)
q = SortQuery(select(User), SortType.ASC, {"name": User.name}, "name", null_last=False)

# descending, NULLs last
q2 = SortQuery(select(User), SortType.DESC, {"name": User.name}, "name", null_last=True)
```

If `sort_field` is not in `table_fields_relation`, `_use_extension()` will raise `KeyError` — this makes invalid input
explicit.

### Pagination

```python
from sqlalchemy_querytools import PaginationQuery

page = PaginationQuery(select(User), offset=20, limit=10)
stmt = page.build()
rows = session.execute(stmt).scalars().all()
```

### Compose: search + sort + paginate

```python
stmt = select(User)
stmt = SearchQuery(stmt, SearchType.ALL_FIELDS, table_fields, "alice").build()
stmt = SortQuery(stmt, SortType.ASC, table_fields, "name", null_last=True).build()
stmt = PaginationQuery(stmt, offset=0, limit=25).build()
rows = session.execute(stmt).scalars().all()
```

---

## Tests

Project includes `pytest` tests which demonstrate expected behaviors:

- Case-insensitive partial search
- Unicode / Cyrillic handling
- Special characters and emoji support
- Date searching behavior (including tests that skip if implementation raises `ValueError`)
- Sorting behavior with `NULL` values

Run tests:

```bash
pip install -r requirements_dev.txt  # sqlalchemy, pytest, etc.
pytest -q
```

---

## Notes / gotchas

- `ilike` and case-insensitivity depend on your DB backend and column collations.
- `SearchQuery` casts non-text fields to `String` for `ALL_FIELDS` search; ensure `table_fields_relation` lists only
  intended columns to search.
- Date searching uses `datetime.fromisoformat`; invalid input raises `ValueError`. Tests are aware of this behavior.
- Tools return `Select` objects; you must execute them with your session (e.g. `session.execute(stmt).scalars().all()`).
- `SortQuery` intentionally raises `KeyError` for missing fields to fail fast with user-provided sort parameters.

---

## Contributing

1. Fork the repo.
2. Create a branch for your change.
3. Add tests for new behaviors or fixes.
4. Open a pull request.

Please include tests for DB-sensitive behavior (e.g. collation, null ordering) where applicable.

---

## License

This project is licensed under the MIT License — see `LICENSE` in the repository for the full text.

```
MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```
