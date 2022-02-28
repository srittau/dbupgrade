from io import StringIO
from unittest.mock import Mock, call

import pytest
from pytest_mock import MockerFixture
from sqlalchemy.exc import SQLAlchemyError

from dbupgrade.apply import apply_file, apply_files
from dbupgrade.files import FileInfo


class TestApplyFiles:
    @pytest.fixture(autouse=True)
    def apply(self, mocker: MockerFixture) -> Mock:
        return mocker.patch("dbupgrade.apply.apply_file")

    def test_apply_none(self, apply: Mock) -> None:
        result = apply_files("", [])
        assert result == ([], None)
        apply.assert_not_called()

    def test_apply_multiple_success(self, apply: Mock) -> None:
        f1 = FileInfo("foo.sql", "schema", "dialect", 123, 14)
        f2 = FileInfo("bar.sql", "schema", "dialect", 124, 15)
        result = apply_files("invalid:///", [f1, f2])
        assert result == ([f1, f2], None)
        apply.assert_has_calls(
            [call("invalid:///", f1), call("invalid:///", f2)]
        )

    def test_apply_multiple_fail(self, apply: Mock) -> None:
        def apply_impl(url: str, file_info: FileInfo) -> None:
            if file_info == f2:
                raise SQLAlchemyError

        apply.side_effect = apply_impl
        f1 = FileInfo("foo.sql", "schema", "dialect", 123, 14)
        f2 = FileInfo("bar.sql", "schema", "dialect", 124, 15)
        f3 = FileInfo("not-called.sql", "schema", "dialect", 125, 15)
        result = apply_files("invalid:///", [f1, f2, f3])
        assert result == ([f1], f2)
        apply.assert_has_calls(
            [call("invalid:///", f1), call("invalid:///", f2)]
        )


class TestApplyFile:
    @pytest.fixture(autouse=True)
    def open(self, mocker: MockerFixture) -> Mock:
        return mocker.patch("dbupgrade.apply.open")

    @pytest.fixture(autouse=True)
    def logging(self, mocker: MockerFixture) -> Mock:
        return mocker.patch("dbupgrade.apply.logging")

    @pytest.fixture(autouse=True)
    def update_sql(self, mocker: MockerFixture) -> Mock:
        return mocker.patch("dbupgrade.apply.update_sql")

    def test_log(self, logging: Mock) -> None:
        info = FileInfo("/foo/bar", "myschema", "sqlite", 45, 3)
        apply_file("sqlite:///", info)
        logging.info.assert_called_once_with("applying #45 (API level 3)")

    def test_execute__with_transaction(
        self, open: Mock, update_sql: Mock
    ) -> None:
        open.return_value = StringIO("")
        info = FileInfo("/foo/bar", "myschema", "sqlite", 45, 3)
        info.transaction = True
        apply_file("sqlite:///", info)
        open.assert_called_once_with("/foo/bar", "r")
        update_sql.assert_called_once_with(
            "sqlite:///", "", "myschema", 45, 3, transaction=True
        )

    def test_execute__without_transaction(
        self, open: Mock, update_sql: Mock
    ) -> None:
        open.return_value = StringIO("")
        info = FileInfo("/foo/bar", "myschema", "sqlite", 45, 3)
        info.transaction = False
        apply_file("sqlite:///", info)
        open.assert_called_once_with("/foo/bar", "r")
        update_sql.assert_called_once_with(
            "sqlite:///", "", "myschema", 45, 3, transaction=False
        )
