from io import StringIO

from dectest import TestCase, test, before

from dbupgrade.apply import apply_file
from dbupgrade.files import FileInfo


class ApplyFileTest(TestCase):
    @before
    def setup_patches(self) -> None:
        self._open = self.patch("dbupgrade.apply.open")
        self._logging = self.patch("dbupgrade.apply.logging")
        self._execute_stream = self.patch("dbupgrade.apply.execute_stream")

    @test
    def log(self) -> None:
        info = FileInfo("/foo/bar", "myschema", "sqlite", 45, 3)
        apply_file("sqlite:///", info)
        self._logging.info.assert_called_once_with(
            "applying #45 (API level 3)"
        )

    @test
    def execute__with_transaction(self) -> None:
        stream = StringIO("")
        self._open.return_value = stream
        info = FileInfo("/foo/bar", "myschema", "sqlite", 45, 3)
        info.transaction = True
        apply_file("sqlite:///", info)
        self._open.assert_called_once_with("/foo/bar", "r")
        self._execute_stream.assert_called_once_with(
            "sqlite:///", stream, "myschema", 45, 3, transaction=True
        )

    @test
    def execute__without_transaction(self) -> None:
        stream = StringIO("")
        self._open.return_value = stream
        info = FileInfo("/foo/bar", "myschema", "sqlite", 45, 3)
        info.transaction = False
        apply_file("sqlite:///", info)
        self._open.assert_called_once_with("/foo/bar", "r")
        self._execute_stream.assert_called_once_with(
            "sqlite:///", stream, "myschema", 45, 3, transaction=False
        )
