from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture

from dbupgrade.args import Arguments
from dbupgrade.main import main


class TestMain:
    @pytest.fixture(autouse=True)
    def logging(self, mocker: MockerFixture) -> Mock:
        logging = mocker.patch("dbupgrade.main.logging")
        logging.INFO = logging.INFO
        logging.WARNING = logging.WARNING
        return logging

    @pytest.fixture(autouse=True)
    def parse_args(self, mocker: MockerFixture) -> Mock:
        args = Arguments("myschema", "sqlite:///", "/tmp")
        return mocker.patch("dbupgrade.main.parse_args", return_value=args)

    @pytest.fixture(autouse=True)
    def db_upgrade(self, mocker: MockerFixture) -> Mock:
        return mocker.patch("dbupgrade.main.db_upgrade")

    def test_default_logging(self, logging: Mock, parse_args: Mock) -> None:
        parse_args.return_value.quiet = False
        main()
        logging.basicConfig.assert_called_once_with(level=logging.INFO)

    def test_quiet_mode(self, logging: Mock, parse_args: Mock) -> None:
        parse_args.return_value.quiet = True
        main()
        logging.basicConfig.assert_called_once_with(level=logging.WARNING)
