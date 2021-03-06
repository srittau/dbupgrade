from typing import Any, Sequence
from unittest.mock import MagicMock, Mock, call

from asserts import (
    assert_equal,
    assert_is_instance,
    assert_raises,
    assert_true,
)
from dectest import TestCase, before, test
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


class FetchCurrentDBVersionsTest(TestCase):
    @before
    def setup_patches(self) -> None:
        engine = MagicMock()
        engine.dialect.name = "sqlite"
        self._create_engine = self.patch("dbupgrade.db.create_engine")
        self._create_engine.return_value = engine
        self._execute = engine.execute

    def _assert_execute_any_call(self, expected_query: str) -> None:
        assert_true(
            any(
                str(c[0][0]) == expected_query
                for c in self._execute.call_args_list
            )
        )

    def _assert_execute_has_calls(
        self, expected_queries: Sequence[Any]
    ) -> None:
        assert_equal(len(expected_queries), len(self._execute.call_args_list))
        for c, ca in zip(expected_queries, self._execute.call_args_list):
            cac = call(str(ca[0][0]), **ca[1])
            assert_equal(c, cac)

    @test
    def create_engine_called(self) -> None:
        fetch_current_db_versions("sqlite:///", "myschema")
        self._create_engine.assert_called_once_with("sqlite:///")
        self._create_engine.return_value.dispose.assert_called_once_with()

    @test
    def dispose_engine_on_error(self) -> None:
        self._execute.side_effect = ValueError()
        with assert_raises(ValueError):
            fetch_current_db_versions("sqlite:///", "myschema")
        self._create_engine.return_value.dispose.assert_called_once_with()

    @test
    def table_does_not_exist(self) -> None:
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

        self._execute.side_effect = execute
        version, api_level = fetch_current_db_versions(
            "sqlite:///", "myschema"
        )
        assert_equal(-1, version)
        assert_equal(0, api_level)
        self._assert_execute_has_calls(
            [
                call(create_sql),
                call(select_versions, col="myschema"),
                call(insert_versions, schema="myschema"),
            ]
        )

    @test
    def table_has_no_row_for_schema(self) -> None:
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

        self._execute.side_effect = execute
        version, api_level = fetch_current_db_versions(
            "sqlite:///", "myschema"
        )
        assert_equal(-1, version)
        assert_equal(0, api_level)
        self._assert_execute_has_calls(
            [
                call(create_sql),
                call(select_versions, col="myschema"),
                call(insert_versions, schema="myschema"),
            ]
        )

    @test
    def table_has_row(self) -> None:
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

        self._execute.side_effect = execute
        version, api_level = fetch_current_db_versions(
            "sqlite:///", "myschema"
        )
        assert_equal(123, version)
        assert_equal(34, api_level)
        self._assert_execute_has_calls(
            [call(create_sql), call(select_versions, col="myschema")]
        )

    @test
    def mysql_quote_char(self) -> None:
        self._create_engine.return_value.dialect.name = "mysql+foo"
        fetch_current_db_versions("mysql:///", "myschema")
        expected_query = SQL_CREATE_DB_CONFIG.format(quote="`")
        self._assert_execute_any_call(expected_query)


class UpdateSQLTest(TestCase):
    @before
    def setup_patches(self) -> None:
        self.engine = MagicMock()
        self.engine.dialect.name = "sqlite"
        self._create_engine = self.patch("dbupgrade.db.create_engine")
        self._create_engine.return_value = self.engine
        self._set_paramstyle("pyformat")
        self.connection = self.engine.begin.return_value.__enter__.return_value
        self.connection.engine = self.engine
        self._execute = self.connection.execute

    def _set_paramstyle(self, paramstyle: str) -> None:
        self.engine.dialect.paramstyle = paramstyle

    def _assert_execute_has_calls(
        self, execute_mock: Mock, expected_queries: Sequence[Any]
    ) -> None:
        assert_equal(len(expected_queries), len(execute_mock.call_args_list))
        for c, ca in zip(expected_queries, execute_mock.call_args_list):
            cac = call(str(ca[0][0]), **ca[1])
            assert_equal(c, cac)

    @test
    def create_engine_called(self) -> None:
        sql = "SELECT * FROM foo"
        update_sql("sqlite:///", sql, "myschema", 0, 0)
        self._create_engine.assert_called_once_with("sqlite:///")
        self._create_engine.return_value.dispose.assert_called_once_with()

    @test
    def dispose_engine_on_error(self) -> None:
        self._execute.side_effect = ValueError()
        with assert_raises(ValueError):
            sql = "SELECT * FROM foo"
            update_sql("sqlite:///", sql, "myschema", 44, 13)
        self._create_engine.return_value.dispose.assert_called_once_with()

    @test
    def execute_with_transaction(self) -> None:
        sql = "SELECT * FROM foo; SELECT * FROM bar;"
        update_sql("sqlite:///", sql, "myschema", 44, 13, transaction=True)
        self._create_engine.assert_called_once_with("sqlite:///")
        sql2 = SQL_UPDATE_VERSIONS.format(quote='"')
        self._assert_execute_has_calls(
            self._execute,
            [
                call("SELECT * FROM foo"),
                call("SELECT * FROM bar"),
                call(sql2, schema="myschema", version=44, api_level=13),
            ],
        )
        assert_is_instance(self._execute.call_args_list[2][0][0], TextClause)

    @test
    def execute_without_transaction(self) -> None:
        sql = "SELECT * FROM foo; SELECT * FROM bar;"
        update_sql("sqlite:///", sql, "myschema", 44, 13, transaction=False)
        self._create_engine.assert_called_once_with(
            "sqlite:///", isolation_level="AUTOCOMMIT"
        )

    @test
    def escape_percent_signs__paramstyle_pyformat(self) -> None:
        self._set_paramstyle("pyformat")
        sql = "SELECT 1 % 2"
        update_sql("sqlite:///", sql, "myschema", 44, 13)
        sql2 = SQL_UPDATE_VERSIONS.format(quote='"')
        self._assert_execute_has_calls(
            self._execute,
            [
                call("SELECT 1 %% 2"),
                call(sql2, schema="myschema", version=44, api_level=13),
            ],
        )

    @test
    def escape_percent_signs__paramstyle_qmark(self) -> None:
        self._set_paramstyle("qmark")
        sql = "SELECT 1 % 2"
        update_sql("sqlite:///", sql, "myschema", 44, 13)
        sql2 = SQL_UPDATE_VERSIONS.format(quote='"')
        self._assert_execute_has_calls(
            self._execute,
            [
                call("SELECT 1 % 2"),
                call(sql2, schema="myschema", version=44, api_level=13),
            ],
        )
