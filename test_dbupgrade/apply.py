from io import StringIO
from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture

from dbupgrade.apply import apply_file
from dbupgrade.files import FileInfo


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
