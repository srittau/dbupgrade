from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from sqlalchemy import create_engine, text as sa_text
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.exc import SQLAlchemyError

from .sql import split_sql

if TYPE_CHECKING:
    from sqlalchemy import Row

SQL_CREATE_DB_CONFIG = """
    CREATE TABLE db_config(
        {quote}schema{quote} VARCHAR(40) PRIMARY KEY,
        version INTEGER NOT NULL,
        api_level INTEGER NOT NULL
    )
"""

SQL_SELECT_VERSIONS = """
    SELECT version, api_level FROM db_config
        WHERE {quote}schema{quote} = :col
"""

SQL_INSERT_DEFAULT_VERSIONS = """
    INSERT INTO db_config({quote}schema{quote}, version, api_level)
        VALUES(:schema, -1, 0)
"""

SQL_UPDATE_VERSIONS = """
    UPDATE db_config SET version = :version, api_level = :api_level
        WHERE {quote}schema{quote} = :schema
"""


def _quote_char(engine: Engine) -> str:
    dialect = engine.dialect.name.split("+")[0]
    return "`" if dialect == "mysql" else '"'


def _execute_sql_ignore_errors(engine: Engine, query: str) -> None:
    try:
        with engine.begin() as connection:
            connection.execute(sa_text(query))
    except SQLAlchemyError:
        pass


class _EngineContext:
    def __init__(self, db_url: str, **kwargs: Any) -> None:
        self._db_url = db_url
        self._kwargs = kwargs
        self._engine: Engine | None = None

    def __enter__(self) -> Engine:
        self._engine = create_engine(self._db_url, future=True, **self._kwargs)
        return self._engine

    def __exit__(self, *args: object) -> None:
        assert self._engine is not None
        self._engine.dispose()
        self._engine = None


def fetch_current_db_versions(db_url: str, schema: str) -> tuple[int, int]:
    """Return the current version and API level of the database for the
    given schema.

    This function creates the db_config table if it does not exist. It also
    creates a row for the given schema if it does not exist. In both cases
    the returned version and API level is 0.
    """

    with _EngineContext(db_url) as engine:
        return _fetch_or_create_version_info(engine, schema)


def _fetch_or_create_version_info(
    engine: Engine, schema: str
) -> tuple[int, int]:
    _try_creating_db_config_table(engine)
    versions = _try_fetching_version_info_for_schema(engine, schema)
    if versions:
        return versions
    else:
        _insert_default_version_info(engine, schema)
        return -1, 0


def _try_creating_db_config_table(engine: Engine) -> None:
    quote_char = _quote_char(engine)
    query = SQL_CREATE_DB_CONFIG.format(quote=quote_char)
    _execute_sql_ignore_errors(engine, query)


def _try_fetching_version_info_for_schema(
    engine: Engine, schema: str
) -> tuple[int, int] | None:
    sql = SQL_SELECT_VERSIONS.format(quote=_quote_char(engine))
    query = sa_text(sql)
    with engine.begin() as connection:
        result = connection.execute(query, {"col": schema})
        rows: Sequence[Row[tuple[int, int]]] = result.fetchall()
    return (rows[0][0], rows[0][1]) if len(rows) == 1 else None


def _insert_default_version_info(engine: Engine, schema: str) -> None:
    quote_char = _quote_char(engine)
    query = sa_text(SQL_INSERT_DEFAULT_VERSIONS.format(quote=quote_char))
    with engine.begin() as connection:
        connection.execute(query, {"schema": schema})


def update_sql(
    db_url: str,
    sql: str,
    schema: str,
    version: int,
    api_level: int,
    *,
    transaction: bool = True,
) -> None:
    kwargs = {} if transaction else {"isolation_level": "AUTOCOMMIT"}
    with _EngineContext(db_url, **kwargs) as engine:
        with engine.begin() as conn:
            _execute_sql_stream(conn, sql)
            _update_versions(conn, schema, version, api_level)


def _execute_sql_stream(conn: Connection, sql: str) -> None:
    """Run the SQL statements in a stream against a database."""
    for query in split_sql(sql):
        conn.execute(sa_text(query))


def _update_versions(
    conn: Connection, schema: str, version: int, api_level: int
) -> None:
    query = sa_text(SQL_UPDATE_VERSIONS.format(quote=_quote_char(conn.engine)))
    conn.execute(
        query, {"schema": schema, "version": version, "api_level": api_level}
    )
