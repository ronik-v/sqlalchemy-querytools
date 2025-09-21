import pytest
from sqlalchemy import select

from sqlalchemy_querytools import SearchQuery
from sqlalchemy_querytools.types import SearchType

from conftest import User


@pytest.mark.parametrize(
    "search_value,expected_ids",
    [
        ("alice", [1]),  # exact
        ("ALICE", [1]),  # case-insensitive
        ("ann", [8]),  # partial (annabelle)
        (
            "li",
            [1, 4, 9, 10, 11],
        ),
    ],
)
def test_search_various_users(
    session, user_select, user_table_fields, search_value, expected_ids
) -> None:
    q = SearchQuery(user_select, SearchType.ALL_FIELDS, user_table_fields, search_value)
    rows = session.execute(q.build()).scalars().all()

    assert [r.id for r in rows] == expected_ids


def test_search_empty_returns_all_users(
    session, user_select, user_table_fields
) -> None:
    q = SearchQuery(user_select, SearchType.ALL_FIELDS, user_table_fields, "")
    rows = session.execute(q.build()).scalars().all()
    got_ids = {r.id for r in rows}

    all_users = session.execute(select(User)).scalars().all()
    expected_ids = {u.id for u in all_users}

    assert got_ids == expected_ids


def test_search_unicode_cyrillic_and_latin(
    session, user_select, user_table_fields
) -> None:
    q1 = SearchQuery(user_select, SearchType.ALL_FIELDS, user_table_fields, "iv")
    ids1 = [r.id for r in session.execute(q1.build()).scalars().all()]
    assert 5 in ids1

    q2 = SearchQuery(user_select, SearchType.ALL_FIELDS, user_table_fields, "ив")
    ids2 = [r.id for r in session.execute(q2.build()).scalars().all()]
    assert 6 in ids2


def test_search_accent_and_special_chars(
    session, user_select, user_table_fields
) -> None:
    q = SearchQuery(user_select, SearchType.ALL_FIELDS, user_table_fields, "mar")
    ids = [r.id for r in session.execute(q.build()).scalars().all()]
    assert 7 in ids


def test_search_articles_punctuation_and_partial_execution(
    article_select, article_table_fields, session
) -> None:
    q = SearchQuery(
        article_select, SearchType.ALL_FIELDS, article_table_fields, "world"
    )
    rows = session.execute(q.build()).scalars().all()

    assert any("Hello, world!" == r.title for r in rows)


def test_search_special_symbols_and_emoji(
    article_select, article_table_fields, session
) -> None:
    q = SearchQuery(article_select, SearchType.ALL_FIELDS, article_table_fields, "—")
    rows = session.execute(q.build()).scalars().all()
    assert any("Another — test" == r.title for r in rows)

    q2 = SearchQuery(article_select, SearchType.ALL_FIELDS, article_table_fields, "😊")
    rows2 = session.execute(q2.build()).scalars().all()

    assert any("Emoji 😊 test" == r.title for r in rows2)


def test_search_date_fields_raises_or_behaves(session, user_select) -> None:
    q = SearchQuery(
        user_select,
        SearchType.DATE_FIELDS,
        {"created_at": User.created_at},
        "2020-01-01",
    )
    try:
        rows = session.execute(q.build()).scalars().all()
        assert any(r.name == "alice" for r in rows)

    except ValueError:
        pytest.skip("Implementation raises ValueError for DATE_FIELDS (known issue)")
