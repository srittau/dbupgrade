from typing import Any, Sequence
from unittest import TestCase
from unittest.mock import patch, call, Mock

from asserts import assert_true, assert_equal, assert_raises

from sqlalchemy.exc import OperationalError
from sqlalchemy.sql.elements import TextClause

from dbupgrade.db import fetch_current_db_versions, SQL_CREATE_DB_CONFIG, \
    SQL_SELECT_VERSIONS, SQL_INSERT_DEFAULT_VERSIONS


class FetchCurrentDBVersionsTest(TestCase):

    def setUp(self) -> None:
        self._create_engine_patch = patch("dbupgrade.db.create_engine")
        self._create_engine = self._create_engine_patch.start()
        self._create_engine.return_value.dialect.name = "sqlite"
        self._execute = self._create_engine.return_value.execute

    def tearDown(self) -> None:
        self._create_engine.stop()

    def _assert_execute_any_call(self, expected_query: str) -> None:
        assert_true(any(str(c[0][0]) == expected_query
                        for c in self._execute.call_args_list))

    def _assert_execute_has_calls(self, expected_queries: Sequence[Any]) \
            -> None:
        assert_equal(len(expected_queries), len(self._execute.call_args_list))
        for c, ca in zip(expected_queries, self._execute.call_args_list):
            cac = call(str(ca[0][0]), **ca[1])
            assert_equal(c, cac)

    def test_engine(self) -> None:
        fetch_current_db_versions("sqlite:///", "myschema")
        self._create_engine.assert_called_once_with("sqlite:///")
        self._create_engine.return_value.dispose.assert_called_once()

    def test_dispose_engine_on_error(self) -> None:
        self._execute.side_effect = ValueError()
        with assert_raises(ValueError):
            fetch_current_db_versions("sqlite:///", "myschema")
        self._create_engine.return_value.dispose.assert_called_once()

    def test_table_does_not_exist(self) -> None:
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
                raise AssertionError(f"unexpected SQL '{sql}'")

        self._execute.side_effect = execute
        version, api_level = \
            fetch_current_db_versions("sqlite:///", "myschema")
        assert_equal(-1, version)
        assert_equal(0, api_level)
        self._assert_execute_has_calls([
            call(create_sql),
            call(select_versions, col="myschema"),
            call(insert_versions, schema="myschema"),
        ])

    def test_table_has_no_row_for_schema(self) -> None:
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
                raise AssertionError(f"unexpected SQL '{sql}'")

        self._execute.side_effect = execute
        version, api_level = \
            fetch_current_db_versions("sqlite:///", "myschema")
        assert_equal(-1, version)
        assert_equal(0, api_level)
        self._assert_execute_has_calls([
            call(create_sql),
            call(select_versions, col="myschema"),
            call(insert_versions, schema="myschema"),
        ])

    def test_table_has_row(self) -> None:
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
                raise AssertionError(f"unexpected SQL '{sql}'")

        self._execute.side_effect = execute
        version, api_level = \
            fetch_current_db_versions("sqlite:///", "myschema")
        assert_equal(123, version)
        assert_equal(34, api_level)
        self._assert_execute_has_calls([
            call(create_sql),
            call(select_versions, col="myschema"),
        ])

    def test_mysql_quote_char(self) -> None:
        self._create_engine.return_value.dialect.name = "mysql+foo"
        fetch_current_db_versions("mysql:///", "myschema")
        expected_query = SQL_CREATE_DB_CONFIG.format(quote="`")
        self._assert_execute_any_call(expected_query)
