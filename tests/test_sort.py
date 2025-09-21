import pytest

from sqlalchemy_querytools import SortQuery
from sqlalchemy_querytools.types import SortType


def names_from_stmt(session, stmt):
    return [u.name for u in session.execute(stmt).scalars().all()]


@pytest.mark.parametrize("null_last", [None, True, False])
def test_sort_various_nulls(session, user_select, user_table_fields, null_last) -> None:
    q = SortQuery(
        user_select, SortType.ASC, user_table_fields, "name", null_last=null_last
    )
    names = names_from_stmt(session, q.build())
    non_nulls = [n for n in names if n is not None]
    assert non_nulls == sorted(non_nulls)


def test_sort_desc(session, user_select, user_table_fields) -> None:
    q = SortQuery(user_select, SortType.DESC, user_table_fields, "name")
    names = [n for n in names_from_stmt(session, q.build()) if n is not None]
    assert names == sorted(names, reverse=True)


def test_sort_missing_field_raises(session, user_select, user_table_fields) -> None:
    with pytest.raises(KeyError):
        SortQuery(
            user_select,
            SortType.ASC,
            user_table_fields,
            "not_exist_field",
        )._use_extension()
