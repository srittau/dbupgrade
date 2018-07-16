import logging

from dectest import TestCase, test, before

from dbupgrade.args import Arguments
from dbupgrade.main import main


class MainTest(TestCase):
    @before
    def setup_patches(self) -> None:
        self.args = Arguments("myschema", "sqlite:///", "/tmp")
        self.logging = self.patch("dbupgrade.main.logging")
        self.logging.INFO = logging.INFO
        self.logging.WARNING = logging.WARNING
        self.parse_args = self.patch("dbupgrade.main.parse_args")
        self.parse_args.return_value = self.args
        self.db_upgrade = self.patch("dbupgrade.main.db_upgrade")

    @test
    def default_logging(self) -> None:
        self.args.quiet = False
        main()
        self.logging.basicConfig.assert_called_once_with(level=logging.INFO)

    @test
    def quiet_mode(self) -> None:
        self.args.quiet = True
        main()
        self.logging.basicConfig.assert_called_once_with(level=logging.WARNING)
