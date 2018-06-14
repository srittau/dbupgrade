from io import StringIO
from unittest import TestCase
from unittest.mock import patch, mock_open

from dbupgrade.apply import apply_file
from dbupgrade.files import FileInfo


class ApplyFileTest(TestCase):
    def setUp(self) -> None:
        self._open_patch = patch("dbupgrade.apply.open")
        self._open = self._open_patch.start()
        self._logging_patch = patch("dbupgrade.apply.logging")
        self._logging = self._logging_patch.start()
        self._execute_patch = patch("dbupgrade.apply.execute_stream")
        self._execute_stream = self._execute_patch.start()

    def tearDown(self) -> None:
        self._open_patch.stop()
        self._logging_patch.stop()
        self._execute_patch.stop()

    def test_log(self) -> None:
        info = FileInfo("/foo/bar", "myschema", "sqlite", 45, 3)
        apply_file("sqlite:///", info)
        self._logging.info.assert_called_once_with(
            "applying #45 (API level 3)")

    def test_execute__with_transaction(self) -> None:
        stream = StringIO("")
        self._open.return_value = stream
        info = FileInfo("/foo/bar", "myschema", "sqlite", 45, 3)
        info.transaction = True
        apply_file("sqlite:///", info)
        self._open.assert_called_once_with("/foo/bar", "r")
        self._execute_stream.assert_called_once_with(
            "sqlite:///", stream, "myschema", 45, 3, transaction=True)

    def test_execute__without_transaction(self) -> None:
        stream = StringIO("")
        self._open.return_value = stream
        info = FileInfo("/foo/bar", "myschema", "sqlite", 45, 3)
        info.transaction = False
        apply_file("sqlite:///", info)
        self._open.assert_called_once_with("/foo/bar", "r")
        self._execute_stream.assert_called_once_with(
            "sqlite:///", stream, "myschema", 45, 3, transaction=False)
