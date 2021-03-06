import os.path
from io import StringIO
from typing import TextIO
from unittest.mock import ANY, call, mock_open, patch

from asserts import (
    assert_equal,
    assert_false,
    assert_raises_regex,
    assert_true,
)
from dectest import TestCase, test

from dbupgrade.files import FileInfo
from dbupgrade.sql_file import ParseError, parse_sql_files, parse_sql_stream


class ParseSQLFilesTest(TestCase):
    def _create_file_info(self) -> FileInfo:
        return FileInfo("", "myschema", "sqlite", 0, 0)

    @test
    def no_files(self) -> None:
        files = parse_sql_files([])
        assert_equal([], files)

    @test
    def parse(self) -> None:
        file_info = self._create_file_info()

        def my_parse_stream(stream: TextIO, _: str) -> FileInfo:
            assert_equal("file content", stream.read())
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
        assert_equal([file_info, file_info], files)

    @test
    def skip_files_with_parse_errors(self) -> None:
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
        assert_equal([file_info], files)


class ParseSQLStreamTest(TestCase):
    @test
    def required_headers(self) -> None:
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
        assert_equal("/foo/bar", info.filename)
        assert_equal("my-schema", info.schema)
        assert_equal("sqlite", info.dialect)
        assert_equal(13, info.version)
        assert_equal(3, info.api_level)
        assert_true(info.transaction)

    @test
    def transaction_yes(self) -> None:
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
        assert_true(info.transaction)

    @test
    def transaction_no(self) -> None:
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
        assert_false(info.transaction)

    @test
    def schema_missing(self) -> None:
        with assert_raises_regex(ParseError, "missing header: schema"):
            parse_sql_stream(
                StringIO(
                    """-- Dialect: sqlite
-- Version: 13
-- API-Level: 3
            """
                ),
                "",
            )

    @test
    def dialect_missing(self) -> None:
        with assert_raises_regex(ParseError, "missing header: dialect"):
            parse_sql_stream(
                StringIO(
                    """-- Schema: my-schema
-- Version: 13
-- API-Level: 3
            """
                ),
                "",
            )

    @test
    def version_missing(self) -> None:
        with assert_raises_regex(ParseError, "missing header: version"):
            parse_sql_stream(
                StringIO(
                    """-- Schema: my-schema
-- Dialect: sqlite
-- API-Level: 3
            """
                ),
                "",
            )

    @test
    def version_is_not_an_int(self) -> None:
        with assert_raises_regex(
            ParseError, "header is not an integer: version"
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

    @test
    def api_level_missing(self) -> None:
        with assert_raises_regex(ParseError, "missing header: api-level"):
            parse_sql_stream(
                StringIO(
                    """-- Schema: my-schema
-- Dialect: sqlite
-- Version: 3
            """
                ),
                "",
            )

    @test
    def api_level_is_not_an_int(self) -> None:
        with assert_raises_regex(
            ParseError, "header is not an integer: api-level"
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

    @test
    def transaction_invalid(self) -> None:
        with assert_raises_regex(
            ParseError, "header must be 'yes' or 'no': transaction"
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

    @test
    def ignore_headers_after_break(self) -> None:
        with assert_raises_regex(ParseError, "missing header: api-level"):
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
