import os
from datetime import datetime, date

import pytest
from sqlalchemy import create_engine, text, select
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg2://postgres:kali@localhost:5432/test_db",
)

engine = create_engine(TEST_DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, future=True)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(nullable=True)


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    user_id: Mapped[int] = mapped_column(nullable=False)
    published_at: Mapped[date] = mapped_column(nullable=True)


def make_users() -> list[User]:
    return [
        User(name="alice", created_at=datetime(2020, 1, 1)),
        User(name=None, created_at=datetime(2021, 6, 1)),
        User(name="bob", created_at=datetime(2022, 3, 15)),
        User(name="charlie", created_at=None),
        User(name="ivan", created_at=datetime(2020, 12, 12)),  # latin
        User(name="иван", created_at=datetime(2021, 5, 5)),  # cyrillic
        User(name="maría", created_at=datetime(2021, 7, 7)),  # accent
        User(name="annabelle", created_at=datetime(2020, 9, 9)),
        User(name="liam", created_at=None),
        User(name="olivia", created_at=datetime(2022, 2, 2)),
        User(name="lisi", created_at=datetime(2023, 3, 3)),
        User(name=None, created_at=None),
    ]


def make_articles() -> list[Article]:
    """
    Returns a list of Article instances with varied titles (punctuation, em-dash, partials).
    """
    return [
        Article(title="Post A", user_id=1, published_at=date(2020, 1, 2)),
        Article(title="Hello, world!", user_id=1, published_at=date(2020, 2, 2)),
        Article(title="Another — test", user_id=2, published_at=None),
        Article(title="Lorem ipsum", user_id=3, published_at=date(2022, 4, 1)),
        Article(title="Null title test", user_id=4, published_at=None),
        Article(title="Z article", user_id=5, published_at=date(2023, 8, 1)),
        Article(title="Alpha", user_id=3, published_at=date(2021, 9, 9)),
        Article(title="Beta", user_id=2, published_at=date(2022, 12, 12)),
        Article(title="Gamma", user_id=1, published_at=None),
        Article(title="Delta", user_id=5, published_at=date(2023, 1, 1)),
        Article(title="Substr test one", user_id=6, published_at=date(2020, 5, 5)),
        Article(title="Substr two", user_id=7, published_at=date(2021, 6, 6)),
        Article(title="Café memories", user_id=8, published_at=date(2020, 7, 7)),
        Article(title="Números 123", user_id=9, published_at=None),
        Article(title="Emoji 😊 test", user_id=10, published_at=date(2022, 8, 8)),
        Article(title="dash-test", user_id=11, published_at=None),
        Article(title="—em dash leading", user_id=1, published_at=date(2021, 1, 1)),
        Article(
            title="edge-case: punctuation!", user_id=2, published_at=date(2021, 2, 2)
        ),
        Article(title="partial-match-li", user_id=3, published_at=date(2022, 10, 10)),
        Article(title="Final article", user_id=4, published_at=date(2023, 11, 11)),
    ]


# ---------- fixtures ----------
@pytest.fixture(scope="session")
def db_engine():
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture()
def session(db_engine):
    s = SessionLocal()
    s.execute(text("TRUNCATE TABLE articles RESTART IDENTITY CASCADE;"))
    s.execute(text("TRUNCATE TABLE users RESTART IDENTITY CASCADE;"))
    s.commit()

    users = make_users()
    s.add_all(users)
    s.flush()

    articles = make_articles()
    s.add_all(articles)
    s.commit()

    try:
        yield s
    finally:
        s.rollback()
        s.close()


@pytest.fixture
def user_select():
    return select(User)


@pytest.fixture
def article_select():
    return select(Article)


@pytest.fixture
def user_table_fields():
    return {"id": User.id, "name": User.name, "created_at": User.created_at}


@pytest.fixture
def article_table_fields():
    return {
        "id": Article.id,
        "title": Article.title,
        "user_id": Article.user_id,
        "published_at": Article.published_at,
    }


@pytest.fixture
def get_non_null_user_names(session):
    def _():
        return [
            u.name
            for u in session.execute(select(User)).scalars().all()
            if u.name is not None
        ]

    return _


@pytest.fixture
def names_from_stmt(session):
    def _names(stmt):
        return [r.name for r in session.execute(stmt).scalars().all()]

    return _names
