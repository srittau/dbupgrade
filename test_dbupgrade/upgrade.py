from unittest.mock import ANY, Mock, patch

import pytest
from pytest_mock import MockerFixture

from dbupgrade.args import Arguments
from dbupgrade.files import FileInfo
from dbupgrade.upgrade import db_upgrade


class TestDBUpgrade:
    @pytest.fixture(autouse=True)
    def logging(self, mocker: MockerFixture) -> Mock:
        return mocker.patch("dbupgrade.upgrade.logging")

    @pytest.fixture(autouse=True)
    def fetch_current_db_versions(self, mocker: MockerFixture) -> Mock:
        return mocker.patch(
            "dbupgrade.upgrade.fetch_current_db_versions",
            return_value=(0, 0),
        )

    @pytest.fixture(autouse=True)
    def collect_sql_files(self, mocker: MockerFixture) -> Mock:
        return mocker.patch(
            "dbupgrade.upgrade.collect_sql_files",
            return_value=[],
        )

    @pytest.fixture(autouse=True)
    def parse_sql_files(self, mocker: MockerFixture) -> Mock:
        return mocker.patch(
            "dbupgrade.upgrade.parse_sql_files",
            return_value=[],
        )

    @pytest.fixture(autouse=True)
    def apply_files(self, mocker: MockerFixture) -> Mock:
        return mocker.patch("dbupgrade.upgrade.apply_files")

    def _create_arguments(
        self,
        *,
        schema: str = "testschema",
        db_url: str = "postgres://localhost/foo",
        script_path: str = "/tmp"
    ) -> Arguments:
        return Arguments(
            schema, db_url, script_path, None, None, ignore_api_level=True
        )

    def test_exercise(
        self,
        fetch_current_db_versions: Mock,
        collect_sql_files: Mock,
        parse_sql_files: Mock,
        apply_files: Mock,
    ) -> None:
        filenames = ["/tmp/foo", "/tmp/bar"]
        file_infos = [FileInfo("", "myschema", "postgres", 150, 30)]
        args = self._create_arguments(
            schema="myschema",
            db_url="postgres://localhost/foo",
            script_path="/tmp",
        )
        fetch_current_db_versions.return_value = 123, 44
        collect_sql_files.return_value = filenames
        parse_sql_files.return_value = file_infos
        db_upgrade(args)
        fetch_current_db_versions.assert_called_once_with(
            "postgres://localhost/foo", "myschema"
        )
        collect_sql_files.assert_called_once_with("/tmp")
        parse_sql_files.assert_called_once_with(filenames)
        apply_files.assert_called_once_with(
            "postgres://localhost/foo", file_infos
        )

    def test_filter(
        self,
        fetch_current_db_versions: Mock,
        parse_sql_files: Mock,
        apply_files: Mock,
    ) -> None:
        args = self._create_arguments()
        fetch_current_db_versions.return_value = 130, 34
        file_info = FileInfo("", "myschema", "", 0, 0)
        parse_sql_files.return_value = [
            file_info,
            FileInfo("", "otherschema", "", 0, 0),
        ]
        with patch("dbupgrade.upgrade.filter_from_arguments") as ffa:
            ffa.return_value.matches = lambda fi: fi.schema == "myschema"
            db_upgrade(args)
            ffa.assert_called_once_with(args, 131, 34)
            apply_files.assert_called_once_with(ANY, [file_info])

    def test_order(self, parse_sql_files: Mock, apply_files: Mock) -> None:
        args = self._create_arguments()
        fi123 = FileInfo("", "myschema", "postgres", 123, 0)
        fi122 = FileInfo("", "myschema", "postgres", 122, 0)
        fi124 = FileInfo("", "myschema", "postgres", 124, 0)
        parse_sql_files.return_value = [fi123, fi122, fi124]
        with patch("dbupgrade.upgrade.filter_from_arguments") as ffa:
            ffa.return_value.matches.return_value = True
            db_upgrade(args)
            apply_files.assert_called_once_with(ANY, [fi122, fi123, fi124])

    def test_log(self, logging: Mock, fetch_current_db_versions: Mock) -> None:
        args = self._create_arguments()
        fetch_current_db_versions.return_value = 123, 44
        db_upgrade(args)
        logging.info.assert_called_once_with(
            "current version: 123, current API level: 44"
        )
