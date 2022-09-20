import json
import logging
from unittest.mock import Mock

import pytest
from pytest import CaptureFixture
from pytest_mock import MockerFixture

from dbupgrade.args import Arguments
from dbupgrade.files import FileInfo
from dbupgrade.main import main
from dbupgrade.result import UpgradeResult, VersionResult

vi = VersionResult(0, 0)


class TestMain:
    @pytest.fixture(autouse=True)
    def logging(self, mocker: MockerFixture) -> Mock:
        logging_mock = mocker.patch("dbupgrade.main.logging")
        logging_mock.INFO = logging.INFO
        logging_mock.WARNING = logging.WARNING
        return logging_mock

    @pytest.fixture(autouse=True)
    def parse_args(self, mocker: MockerFixture) -> Mock:
        args = Arguments("myschema", "sqlite:///", "/tmp")
        return mocker.patch("dbupgrade.main.parse_args", return_value=args)

    @pytest.fixture(autouse=True)
    def db_upgrade(self, mocker: MockerFixture) -> Mock:
        return mocker.patch(
            "dbupgrade.main.db_upgrade", return_value=UpgradeResult(vi, vi, [])
        )

    def test_success(self, db_upgrade: Mock) -> None:
        db_upgrade.return_value = UpgradeResult(
            vi, vi, [FileInfo("foo.sql", "", "", 123, 45)]
        )
        main()

    def test_error(self, db_upgrade: Mock) -> None:
        db_upgrade.return_value = UpgradeResult(
            vi, vi, [], FileInfo("foo.sql", "", "", 123, 45)
        )
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 1

    def test_default_logging(self, logging: Mock, parse_args: Mock) -> None:
        parse_args.return_value.quiet = False
        parse_args.return_value.json = False
        main()
        logging.basicConfig.assert_called_once_with(level=logging.INFO)

    def test_quiet_logging(self, logging: Mock, parse_args: Mock) -> None:
        parse_args.return_value.quiet = True
        main()
        logging.basicConfig.assert_called_once_with(level=logging.WARNING)

    def test_json_logging(self, logging: Mock, parse_args: Mock) -> None:
        parse_args.return_value.json = True
        main()
        logging.basicConfig.assert_called_once_with(level=logging.ERROR)

    def test_no_json_output(
        self, parse_args: Mock, capsys: CaptureFixture
    ) -> None:
        parse_args.return_value.json = False
        main()
        assert capsys.readouterr().out == ""

    def test_json_success(
        self, parse_args: Mock, db_upgrade: Mock, capsys: CaptureFixture
    ) -> None:
        parse_args.return_value.json = True
        db_upgrade.return_value = UpgradeResult(
            VersionResult(123, 45),
            VersionResult(124, 46),
            [FileInfo("foo.sql", "", "", 124, 46)],
        )
        main()
        j = json.loads(capsys.readouterr().out)
        assert j == {
            "success": True,
            "oldVersion": {"version": 123, "apiLevel": 45},
            "newVersion": {"version": 124, "apiLevel": 46},
            "appliedScripts": [
                {
                    "filename": "foo.sql",
                    "version": 124,
                    "apiLevel": 46,
                }
            ],
        }

    def test_json_error(
        self, parse_args: Mock, db_upgrade: Mock, capsys: CaptureFixture
    ) -> None:
        parse_args.return_value.json = True
        db_upgrade.return_value = UpgradeResult(
            VersionResult(123, 45),
            VersionResult(123, 45),
            [],
            FileInfo("foo.sql", "", "", 124, 46),
        )
        with pytest.raises(SystemExit):
            main()
        j = json.loads(capsys.readouterr().out)
        assert j == {
            "success": False,
            "oldVersion": {"version": 123, "apiLevel": 45},
            "newVersion": {"version": 123, "apiLevel": 45},
            "appliedScripts": [],
            "failedScript": {
                "filename": "foo.sql",
                "version": 124,
                "apiLevel": 46,
            },
        }
