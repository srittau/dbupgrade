from __future__ import annotations

import sqlite3
from collections.abc import Generator
from tempfile import NamedTemporaryFile
from typing import Any, Sequence, cast
from unittest.mock import MagicMock, Mock, _Call, call

import pytest
from pytest_mock import MockerFixture
from sqlalchemy.sql.elements import TextClause

from dbupgrade.db import (
    SQL_CREATE_DB_CONFIG,
    SQL_UPDATE_VERSIONS,
    fetch_current_db_versions,
    update_sql,
)


class DBFixtureContext:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self._connection: sqlite3.Connection | None = None

    def __enter__(self) -> sqlite3.Cursor:
        self._connection = sqlite3.connect(self.db_path)
        self._connection.__enter__()
        return self._connection.cursor()

    def __exit__(self, *args: Any) -> None:
        assert self._connection
        self._connection.__exit__(*args)


class DBFixture:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

    @property
    def url(self) -> str:
        return f"sqlite:///{self.db_path}"

    def connect(self) -> DBFixtureContext:
        return DBFixtureContext(self.db_path)

    def create_table(self) -> None:
        with self.connect() as cursor:
            cursor.execute(SQL_CREATE_DB_CONFIG.format(quote='"'))

    def insert_row(self, schema: str, version: int, api_level: int) -> None:
        with self.connect() as cursor:
            cursor.execute(
                """
                INSERT INTO db_config("schema", version, api_level)
                VALUES(?, ?, ?)
                """,
                [schema, version, api_level],
            )

    def fetch_rows(self) -> list[tuple[str, int, int]]:
        with self.connect() as cursor:
            cursor.execute("SELECT * FROM db_config")
            return cursor.fetchall()


@pytest.fixture
def test_db() -> Generator[DBFixture, None, None]:
    with NamedTemporaryFile(prefix="test-", suffix=".sqlite") as f:
        yield DBFixture(f.name)


class TestFetchCurrentDBVersions:
    @pytest.fixture
    def create_engine(self, mocker: MockerFixture) -> Mock:
        engine = MagicMock()
        engine.dialect.name = "sqlite"
        return mocker.patch("dbupgrade.db.create_engine", return_value=engine)

    def _assert_execute_any_call(
        self,
        create_engine: Mock,
        expected_query: str,
    ) -> None:
        execute = create_engine.return_value.begin.return_value.__enter__.return_value.execute
        assert any(
            str(c[0][0]) == expected_query for c in execute.call_args_list
        )

    def test_table_does_not_exist__return_value(
        self, test_db: DBFixture
    ) -> None:
        version, api_level = fetch_current_db_versions(test_db.url, "myschema")
        assert version == -1
        assert api_level == 0

    def test_table_does_not_exist__created(self, test_db: DBFixture) -> None:
        fetch_current_db_versions(test_db.url, "myschema")
        rows = test_db.fetch_rows()
        assert rows == [("myschema", -1, 0)]

    def test_table_has_no_row_for_schema__return_value(
        self, test_db: DBFixture
    ) -> None:
        test_db.create_table()
        version, api_level = fetch_current_db_versions(test_db.url, "myschema")
        assert version == -1
        assert api_level == 0

    def test_table_has_no_row_for_schema__inserted(
        self, test_db: DBFixture
    ) -> None:
        test_db.create_table()
        fetch_current_db_versions(test_db.url, "myschema")
        rows = test_db.fetch_rows()
        assert rows == [("myschema", -1, 0)]

    def test_table_has_row__return_value(self, test_db: DBFixture) -> None:
        test_db.create_table()
        test_db.insert_row("myschema", 123, 34)
        version, api_level = fetch_current_db_versions(test_db.url, "myschema")
        assert version == 123
        assert api_level == 34

    def test_mysql_quote_char(self, create_engine: Mock) -> None:
        create_engine.return_value.dialect.name = "mysql+foo"
        fetch_current_db_versions("mysql:///", "myschema")
        expected_query = SQL_CREATE_DB_CONFIG.format(quote="`")
        self._assert_execute_any_call(create_engine, expected_query)


class TestUpdateSQL:
    @pytest.fixture
    def create_engine(self, mocker: MockerFixture) -> Mock:
        engine = MagicMock()
        engine.dialect.name = "sqlite"
        engine.dialect.paramstyle = "pyformat"
        return mocker.patch("dbupgrade.db.create_engine", return_value=engine)

    @pytest.fixture
    def engine(self, create_engine: Mock) -> Mock:
        return cast(Mock, create_engine.return_value)

    @pytest.fixture
    def connection(self, engine: Mock) -> Mock:
        connection = engine.begin.return_value.__enter__.return_value
        connection.engine = engine
        return cast(Mock, connection)

    def _set_paramstyle(self, create_engine: Mock, paramstyle: str) -> None:
        create_engine.return_value.dialect.paramstyle = paramstyle

    def _assert_execute_has_calls(
        self, execute_mock: Mock, expected_queries: Sequence[_Call]
    ) -> None:
        assert len(execute_mock.call_args_list) == len(expected_queries)
        for expected_call, true_call in zip(
            expected_queries, execute_mock.call_args_list
        ):
            assert len(true_call) == 2, f"unexpected call: {true_call!r}"
            query = str(true_call[0][0])
            true_call2 = call(query, *true_call[0][1:], **true_call[1])
            assert true_call2 == expected_call

    def test_create_engine_called(
        self, create_engine: Mock, engine: Mock
    ) -> None:
        update_sql("sqlite:///", "SELECT * FROM foo", "myschema", 0, 0)
        create_engine.assert_called_once_with("sqlite:///", future=True)
        engine.dispose.assert_called_once_with()

    def test_dispose_engine_on_error(
        self, engine: Mock, connection: Mock
    ) -> None:
        connection.execute.side_effect = ValueError()
        with pytest.raises(ValueError):
            update_sql("sqlite:///", "SELECT * FROM foo", "myschema", 44, 13)
        engine.dispose.assert_called_once_with()

    def test_execute_with_transaction(
        self, create_engine: Mock, connection: Mock
    ) -> None:
        update_sql(
            "sqlite:///",
            "SELECT * FROM foo; SELECT * FROM bar;",
            "myschema",
            44,
            13,
            transaction=True,
        )
        create_engine.assert_called_once_with("sqlite:///", future=True)
        self._assert_execute_has_calls(
            connection.execute,
            [
                call("SELECT * FROM foo"),
                call("SELECT * FROM bar"),
                call(
                    SQL_UPDATE_VERSIONS.format(quote='"'),
                    {"schema": "myschema", "version": 44, "api_level": 13},
                ),
            ],
        )
        assert isinstance(
            connection.execute.call_args_list[2][0][0], TextClause
        )

    def test_execute_without_transaction(self, create_engine: Mock) -> None:
        update_sql(
            "sqlite:///",
            "SELECT * FROM foo; SELECT * FROM bar;",
            "myschema",
            44,
            13,
            transaction=False,
        )
        create_engine.assert_called_once_with(
            "sqlite:///", future=True, isolation_level="AUTOCOMMIT"
        )

    def test_colon(
        self,
        create_engine: Mock,
        connection: Mock,
    ) -> None:
        self._set_paramstyle(create_engine, "pyformat")
        update_sql("sqlite:///", "SELECT ':foo'", "myschema", 44, 13)
        self._assert_execute_has_calls(
            connection.execute,
            [
                call("SELECT ':foo'"),
                call(
                    SQL_UPDATE_VERSIONS.format(quote='"'),
                    {"schema": "myschema", "version": 44, "api_level": 13},
                ),
            ],
        )
