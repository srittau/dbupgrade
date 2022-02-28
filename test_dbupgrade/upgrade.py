from __future__ import annotations

from unittest.mock import ANY, Mock, patch

import pytest
from pytest_mock import MockerFixture

from dbupgrade.files import FileInfo
from dbupgrade.result import UpgradeResult, VersionResult
from dbupgrade.upgrade import db_upgrade
from dbupgrade.version import MAX_VERSION, VersionInfo, VersionMatcher


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
        return mocker.patch(
            "dbupgrade.upgrade.apply_files", return_value=([], None)
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
        fetch_current_db_versions.return_value = 123, 44
        collect_sql_files.return_value = filenames
        parse_sql_files.return_value = file_infos
        db_upgrade(
            "myschema", "postgres://localhost/foo", "/tmp", VersionInfo()
        )
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
        fetch_current_db_versions.return_value = 130, 34
        file_info = FileInfo("", "myschema", "", 0, 0)
        parse_sql_files.return_value = [
            file_info,
            FileInfo("", "otherschema", "", 0, 0),
        ]
        with patch("dbupgrade.upgrade.Filter") as filter_:
            filter_.return_value.matches = lambda fi: fi.schema == "myschema"
            db_upgrade(
                "myschema",
                "postgres://localhost/foo",
                "/tmp",
                VersionInfo(api_level=12),
            )
            filter_.assert_called_once_with(
                "myschema", "postgres", VersionMatcher(131, MAX_VERSION, 12)
            )
            apply_files.assert_called_once_with(ANY, [file_info])

    def test_order(self, parse_sql_files: Mock, apply_files: Mock) -> None:
        fi123 = FileInfo("", "myschema", "postgres", 123, 0)
        fi122 = FileInfo("", "myschema", "postgres", 122, 0)
        fi124 = FileInfo("", "myschema", "postgres", 124, 0)
        parse_sql_files.return_value = [fi123, fi122, fi124]
        with patch("dbupgrade.upgrade.Filter") as filter_:
            filter_.return_value.return_value.matches.return_value = True
            db_upgrade(
                "myschema",
                "postgres://localhost/foo",
                "/tmp",
                VersionInfo(),
            )
            apply_files.assert_called_once_with(ANY, [fi122, fi123, fi124])

    def test_log(self, logging: Mock, fetch_current_db_versions: Mock) -> None:
        fetch_current_db_versions.return_value = 123, 44
        db_upgrade(
            "myschema", "postgres://localhost/foo", "/tmp", VersionInfo()
        )
        logging.info.assert_called_once_with(
            "current version: 123, current API level: 44"
        )

    def test_result_no_files(
        self, fetch_current_db_versions: Mock, apply_files: Mock
    ) -> None:
        fetch_current_db_versions.return_value = (122, 44)
        apply_files.return_value = ([], None)
        result = db_upgrade(
            "myschema",
            "postgres://localhost/foo",
            "/tmp",
            VersionInfo(),
        )
        assert result == UpgradeResult(
            VersionResult(122, 44), VersionResult(122, 44), [], None
        )

    def test_result_success(
        self, fetch_current_db_versions: Mock, apply_files: Mock
    ) -> None:
        file_info1 = FileInfo("foo.sql", "myschema", "", 123, 45)
        file_info2 = FileInfo("foo.sql", "myschema", "", 124, 46)
        fetch_current_db_versions.return_value = (122, 44)
        apply_files.return_value = ([file_info1, file_info2], None)
        result = db_upgrade(
            "myschema",
            "postgres://localhost/foo",
            "/tmp",
            VersionInfo(),
        )
        assert result == UpgradeResult(
            VersionResult(122, 44),
            VersionResult(124, 46),
            [file_info1, file_info2],
            None,
        )

    def test_result_error(
        self, fetch_current_db_versions: Mock, apply_files: Mock
    ) -> None:
        file_info1 = FileInfo("foo.sql", "myschema", "", 123, 45)
        file_info2 = FileInfo("foo.sql", "myschema", "", 124, 46)
        fetch_current_db_versions.return_value = (122, 44)
        apply_files.return_value = ([file_info1], file_info2)
        result = db_upgrade(
            "myschema",
            "postgres://localhost/foo",
            "/tmp",
            VersionInfo(),
        )
        assert result == UpgradeResult(
            VersionResult(122, 44),
            VersionResult(123, 45),
            [file_info1],
            file_info2,
        )
