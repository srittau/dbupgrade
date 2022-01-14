from typing import Any, Sequence, cast
from unittest.mock import MagicMock, Mock, call

import pytest
from pytest_mock import MockerFixture
from sqlalchemy.exc import OperationalError
from sqlalchemy.sql.elements import TextClause

from dbupgrade.db import (
    SQL_CREATE_DB_CONFIG,
    SQL_INSERT_DEFAULT_VERSIONS,
    SQL_SELECT_VERSIONS,
    SQL_UPDATE_VERSIONS,
    fetch_current_db_versions,
    update_sql,
)


class TestFetchCurrentDBVersions:
    @pytest.fixture(autouse=True)
    def create_engine(self, mocker: MockerFixture) -> Mock:
        engine = MagicMock()
        engine.dialect.name = "sqlite"
        return mocker.patch("dbupgrade.db.create_engine", return_value=engine)

    def _assert_execute_any_call(
        self,
        create_engine: Mock,
        expected_query: str,
    ) -> None:
        execute = create_engine.return_value.execute
        assert any(
            str(c[0][0]) == expected_query for c in execute.call_args_list
        )

    def _assert_execute_has_calls(
        self, create_engine: Mock, expected_queries: Sequence[Any]
    ) -> None:
        execute = create_engine.return_value.execute
        assert len(execute.call_args_list) == len(expected_queries)
        for c, ca in zip(expected_queries, execute.call_args_list):
            cac = call(str(ca[0][0]), **ca[1])
            assert cac == c

    def test_create_engine_called(self, create_engine: Mock) -> None:
        fetch_current_db_versions("sqlite:///", "myschema")
        create_engine.assert_called_once_with("sqlite:///")
        create_engine.return_value.dispose.assert_called_once_with()

    def test_dispose_engine_on_error(self, create_engine: Mock) -> None:
        create_engine.return_value.execute.side_effect = ValueError()
        with pytest.raises(ValueError):
            fetch_current_db_versions("sqlite:///", "myschema")
        create_engine.return_value.dispose.assert_called_once_with()

    def test_table_does_not_exist(self, create_engine: Mock) -> None:
        create_sql = SQL_CREATE_DB_CONFIG.format(quote='"')
        select_versions = SQL_SELECT_VERSIONS.format(quote='"')
        insert_versions = SQL_INSERT_DEFAULT_VERSIONS.format(quote='"')

        def execute(sql: TextClause, **_: Any) -> Mock:
            real_sql = str(sql)
            if real_sql == create_sql:
                raise OperationalError(None, None, None)
            elif real_sql == select_versions:
                m = Mock()
                m.fetchall.return_value = []
                return m
            elif real_sql == insert_versions:
                return Mock()
            else:
                raise AssertionError("unexpected SQL '{}'".format(sql))

        create_engine.return_value.execute.side_effect = execute
        version, api_level = fetch_current_db_versions(
            "sqlite:///", "myschema"
        )
        assert version == -1
        assert api_level == 0
        self._assert_execute_has_calls(
            create_engine,
            [
                call(create_sql),
                call(select_versions, col="myschema"),
                call(insert_versions, schema="myschema"),
            ],
        )

    def test_table_has_no_row_for_schema(self, create_engine: Mock) -> None:
        create_sql = SQL_CREATE_DB_CONFIG.format(quote='"')
        select_versions = SQL_SELECT_VERSIONS.format(quote='"')
        insert_versions = SQL_INSERT_DEFAULT_VERSIONS.format(quote='"')

        def execute(sql: TextClause, **_: Any) -> Mock:
            real_sql = str(sql)
            if real_sql == create_sql:
                return Mock()
            elif real_sql == select_versions:
                m = Mock()
                m.fetchall.return_value = []
                return m
            elif real_sql == insert_versions:
                return Mock()
            else:
                raise AssertionError("unexpected SQL '{}'".format(sql))

        create_engine.return_value.execute.side_effect = execute
        version, api_level = fetch_current_db_versions(
            "sqlite:///", "myschema"
        )
        assert version == -1
        assert api_level == 0
        self._assert_execute_has_calls(
            create_engine,
            [
                call(create_sql),
                call(select_versions, col="myschema"),
                call(insert_versions, schema="myschema"),
            ],
        )

    def test_table_has_row(self, create_engine: Mock) -> None:
        create_sql = SQL_CREATE_DB_CONFIG.format(quote='"')
        select_versions = SQL_SELECT_VERSIONS.format(quote='"')

        def execute(sql: TextClause, **_: Any) -> Mock:
            real_sql = str(sql)
            if real_sql == create_sql:
                return Mock()
            elif real_sql == select_versions:
                m = Mock()
                m.fetchall.return_value = [(123, 34)]
                return m
            else:
                raise AssertionError("unexpected SQL '{}'".format(sql))

        create_engine.return_value.execute.side_effect = execute
        version, api_level = fetch_current_db_versions(
            "sqlite:///", "myschema"
        )
        assert version == 123
        assert api_level == 34
        self._assert_execute_has_calls(
            create_engine,
            [call(create_sql), call(select_versions, col="myschema")],
        )

    def test_mysql_quote_char(self, create_engine: Mock) -> None:
        create_engine.return_value.dialect.name = "mysql+foo"
        fetch_current_db_versions("mysql:///", "myschema")
        expected_query = SQL_CREATE_DB_CONFIG.format(quote="`")
        self._assert_execute_any_call(create_engine, expected_query)


class TestUpdateSQL:
    @pytest.fixture(autouse=True)
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
        self, execute_mock: Mock, expected_queries: Sequence[Any]
    ) -> None:
        assert len(execute_mock.call_args_list) == len(expected_queries)
        for c, ca in zip(expected_queries, execute_mock.call_args_list):
            cac = call(str(ca[0][0]), **ca[1])
            assert cac == c

    def test_create_engine_called(
        self, create_engine: Mock, engine: Mock
    ) -> None:
        sql = "SELECT * FROM foo"
        update_sql("sqlite:///", sql, "myschema", 0, 0)
        create_engine.assert_called_once_with("sqlite:///")
        engine.dispose.assert_called_once_with()

    def test_dispose_engine_on_error(
        self, engine: Mock, connection: Mock
    ) -> None:
        connection.execute.side_effect = ValueError()
        with pytest.raises(ValueError):
            sql = "SELECT * FROM foo"
            update_sql("sqlite:///", sql, "myschema", 44, 13)
        engine.dispose.assert_called_once_with()

    def test_execute_with_transaction(
        self, create_engine: Mock, connection: Mock
    ) -> None:
        sql = "SELECT * FROM foo; SELECT * FROM bar;"
        update_sql("sqlite:///", sql, "myschema", 44, 13, transaction=True)
        create_engine.assert_called_once_with("sqlite:///")
        sql2 = SQL_UPDATE_VERSIONS.format(quote='"')
        self._assert_execute_has_calls(
            connection.execute,
            [
                call("SELECT * FROM foo"),
                call("SELECT * FROM bar"),
                call(sql2, schema="myschema", version=44, api_level=13),
            ],
        )
        assert isinstance(
            connection.execute.call_args_list[2][0][0], TextClause
        )

    def test_execute_without_transaction(self, create_engine: Mock) -> None:
        sql = "SELECT * FROM foo; SELECT * FROM bar;"
        update_sql("sqlite:///", sql, "myschema", 44, 13, transaction=False)
        create_engine.assert_called_once_with(
            "sqlite:///", isolation_level="AUTOCOMMIT"
        )

    def test_escape_percent_signs__paramstyle_pyformat(
        self,
        create_engine: Mock,
        connection: Mock,
    ) -> None:
        self._set_paramstyle(create_engine, "pyformat")
        sql = "SELECT 1 % 2"
        update_sql("sqlite:///", sql, "myschema", 44, 13)
        sql2 = SQL_UPDATE_VERSIONS.format(quote='"')
        self._assert_execute_has_calls(
            connection.execute,
            [
                call("SELECT 1 %% 2"),
                call(sql2, schema="myschema", version=44, api_level=13),
            ],
        )

    def test_escape_percent_signs__paramstyle_qmark(
        self,
        create_engine: Mock,
        connection: Mock,
    ) -> None:
        self._set_paramstyle(create_engine, "qmark")
        sql = "SELECT 1 % 2"
        update_sql("sqlite:///", sql, "myschema", 44, 13)
        sql2 = SQL_UPDATE_VERSIONS.format(quote='"')
        self._assert_execute_has_calls(
            connection.execute,
            [
                call("SELECT 1 % 2"),
                call(sql2, schema="myschema", version=44, api_level=13),
            ],
        )
