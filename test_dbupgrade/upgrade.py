from unittest import TestCase
from unittest.mock import patch, ANY

from dbupgrade.args import Arguments
from dbupgrade.files import FileInfo
from dbupgrade.upgrade import db_upgrade


class DBUpgradeTest(TestCase):

    def setUp(self) -> None:
        self._logging_patch = patch("dbupgrade.upgrade.logging")
        self._logging = self._logging_patch.start()
        self._fetch_patch = \
            patch("dbupgrade.upgrade.fetch_current_db_versions")
        self._fetch_current_db_versions = self._fetch_patch.start()
        self._fetch_current_db_versions.return_value = 0, 0
        self._collect_patch = patch("dbupgrade.upgrade.collect_sql_files")
        self._collect_sql_files = self._collect_patch.start()
        self._collect_sql_files.return_value = []
        self._parse_patch = patch("dbupgrade.upgrade.parse_sql_files")
        self._parse_sql_files = self._parse_patch.start()
        self._parse_sql_files.return_value = []
        self._apply_patch = patch("dbupgrade.upgrade.apply_files")
        self._apply_files = self._apply_patch.start()

    def tearDown(self) -> None:
        self._logging_patch.stop()
        self._fetch_patch.stop()
        self._collect_patch.stop()
        self._parse_patch.stop()
        self._apply_patch.stop()

    def _create_arguments(self, *, schema: str = "testschema",
                          db_url: str = "postgres://localhost/foo",
                          script_path: str = "/tmp") -> Arguments:
        return Arguments(schema, db_url, script_path,
                         None, None, ignore_api_level=True)

    def test_exercise(self) -> None:
        filenames = ["/tmp/foo", "/tmp/bar"]
        file_infos = [FileInfo("", "myschema", "postgres", 150, 30)]
        args = self._create_arguments(
            schema="myschema", db_url="postgres://localhost/foo",
            script_path="/tmp")
        self._fetch_current_db_versions.return_value = 123, 44
        self._collect_sql_files.return_value = filenames
        self._parse_sql_files.return_value = file_infos
        db_upgrade(args)
        self._fetch_current_db_versions.assert_called_once_with(
            "postgres://localhost/foo", "myschema")
        self._collect_sql_files.assert_called_once_with("/tmp")
        self._parse_sql_files.assert_called_once_with(filenames)
        self._apply_files.assert_called_once_with(
            "postgres://localhost/foo", file_infos)

    def test_filter(self) -> None:
        args = self._create_arguments()
        self._fetch_current_db_versions.return_value = 130, 34
        file_info = FileInfo("", "myschema", "", 0, 0)
        self._parse_sql_files.return_value = [
            file_info,
            FileInfo("", "otherschema", "", 0, 0),
        ]
        with patch("dbupgrade.upgrade.filter_from_arguments") as ffa:
            ffa.return_value.matches = lambda fi: fi.schema == "myschema"
            db_upgrade(args)
            ffa.assert_called_once_with(args, 131, 34)
            self._apply_files.assert_called_once_with(ANY, [file_info])

    def test_order(self) -> None:
        args = self._create_arguments()
        fi123 = FileInfo("", "myschema", "postgres", 123, 0)
        fi122 = FileInfo("", "myschema", "postgres", 122, 0)
        fi124 = FileInfo("", "myschema", "postgres", 124, 0)
        self._parse_sql_files.return_value = [fi123, fi122, fi124]
        with patch("dbupgrade.upgrade.filter_from_arguments") as ffa:
            ffa.return_value.matches.return_value = True
            db_upgrade(args)
            self._apply_files.assert_called_once_with(
                ANY, [fi122, fi123, fi124])

    def test_log(self) -> None:
        args = self._create_arguments()
        self._fetch_current_db_versions.return_value = 123, 44
        db_upgrade(args)
        self._logging.info.assert_called_once_with(
            "current version: 123, current API level: 44")
