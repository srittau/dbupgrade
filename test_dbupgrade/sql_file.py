import os.path
from io import StringIO
from typing import TextIO
from unittest.mock import ANY, call, mock_open, patch

import pytest

from dbupgrade.files import FileInfo
from dbupgrade.sql_file import ParseError, parse_sql_files, parse_sql_stream


class TestParseSQLFiles:
    def _create_file_info(self) -> FileInfo:
        return FileInfo("", "myschema", "sqlite", 0, 0)

    def test_no_files(self) -> None:
        assert parse_sql_files([]) == []

    def test_parse(self) -> None:
        file_info = self._create_file_info()

        def my_parse_stream(stream: TextIO, _: str) -> FileInfo:
            assert stream.read() == "file content"
            return file_info

        with patch(
            "dbupgrade.sql_file.open", mock_open(read_data="file content")
        ):
            with patch("dbupgrade.sql_file.parse_sql_stream") as parse_stream:
                parse_stream.side_effect = my_parse_stream
                files = parse_sql_files(["foo", "bar"])
                parse_stream.assert_has_calls(
                    [call(ANY, "foo"), call(ANY, "bar")]
                )
        assert files == [file_info, file_info]

    def test_skip_files_with_parse_errors(self) -> None:
        file_info = self._create_file_info()
        with patch(
            "dbupgrade.sql_file.open", mock_open(read_data="file content")
        ):
            with patch("dbupgrade.sql_file.logging") as logging:
                with patch(
                    "dbupgrade.sql_file.parse_sql_stream"
                ) as parse_stream:
                    parse_stream.side_effect = [
                        ParseError("test error"),
                        file_info,
                    ]
                    files = parse_sql_files(
                        [os.path.join("path", "foo"), "bar"]
                    )
                logging.warning.assert_called_once_with("foo: test error")
        assert files == [file_info]


class TestParseSQLStream:
    def test_required_headers(self) -> None:
        info = parse_sql_stream(
            StringIO(
                """-- Schema: my-schema
-- Dialect: sqlite
-- Version: 13
-- API-Level: 3

UPDATE foo SET bar = 99;
        """
            ),
            "/foo/bar",
        )
        assert info.filename == "/foo/bar"
        assert info.schema == "my-schema"
        assert info.dialect == "sqlite"
        assert info.version == 13
        assert info.api_level == 3
        assert info.transaction

    def test_transaction_yes(self) -> None:
        info = parse_sql_stream(
            StringIO(
                """-- Schema: my-schema
-- Dialect: sqlite
-- Version: 25
-- API-Level: 3
-- Transaction: yes
            """
            ),
            "",
        )
        assert info.transaction

    def test_transaction_no(self) -> None:
        info = parse_sql_stream(
            StringIO(
                """-- Schema: my-schema
-- Dialect: sqlite
-- Version: 25
-- API-Level: 3
-- Transaction: no
            """
            ),
            "",
        )
        assert not info.transaction

    def test_schema_missing(self) -> None:
        with pytest.raises(ParseError, match="missing header: schema") as exc:
            parse_sql_stream(
                StringIO(
                    """-- Dialect: sqlite
-- Version: 13
-- API-Level: 3
            """
                ),
                "",
            )

    def test_dialect_missing(self) -> None:
        with pytest.raises(ParseError, match="missing header: dialect"):
            parse_sql_stream(
                StringIO(
                    """-- Schema: my-schema
-- Version: 13
-- API-Level: 3
            """
                ),
                "",
            )

    def test_version_missing(self) -> None:
        with pytest.raises(ParseError, match="missing header: version"):
            parse_sql_stream(
                StringIO(
                    """-- Schema: my-schema
-- Dialect: sqlite
-- API-Level: 3
            """
                ),
                "",
            )

    def test_version_is_not_an_int(self) -> None:
        with pytest.raises(
            ParseError, match="header is not an integer: version"
        ):
            parse_sql_stream(
                StringIO(
                    """-- Schema: my-schema
-- Dialect: sqlite
-- Version: INVALID
-- API-Level: 3
            """
                ),
                "",
            )

    def test_api_level_missing(self) -> None:
        with pytest.raises(ParseError, match="missing header: api-level"):
            parse_sql_stream(
                StringIO(
                    """-- Schema: my-schema
-- Dialect: sqlite
-- Version: 3
            """
                ),
                "",
            )

    def test_api_level_is_not_an_int(self) -> None:
        with pytest.raises(
            ParseError, match="header is not an integer: api-level"
        ):
            parse_sql_stream(
                StringIO(
                    """-- Schema: my-schema
-- Dialect: sqlite
-- Version: 24
-- API-Level: INVALID
            """
                ),
                "",
            )

    def test_transaction_invalid(self) -> None:
        with pytest.raises(
            ParseError, match="header must be 'yes' or 'no': transaction"
        ):
            parse_sql_stream(
                StringIO(
                    """-- Schema: my-schema
-- Dialect: sqlite
-- Version: 25
-- API-Level: 3
-- Transaction: INVALID
            """
                ),
                "",
            )

    def test_ignore_headers_after_break(self) -> None:
        with pytest.raises(ParseError, match="missing header: api-level"):
            parse_sql_stream(
                StringIO(
                    """-- Schema: my-schema
-- Dialect: sqlite
-- Version: 13

-- API-Level: 3
        """
                ),
                "",
            )
