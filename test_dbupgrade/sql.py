import os.path
from io import StringIO
from typing import TextIO
from unittest import TestCase
from unittest.mock import patch, mock_open

from asserts import assert_equal, assert_raises_regex

from dbupgrade.files import FileInfo
from dbupgrade.sql import parse_sql_files, ParseError, parse_sql_stream


class ParseSQLFilesTest(TestCase):

    def _create_file_info(self) -> FileInfo:
        return FileInfo("myschema", "sqlite", 0, 0)

    def test_no_files(self) -> None:
        files = parse_sql_files([])
        assert_equal([], files)

    def test_parse(self) -> None:
        file_info = self._create_file_info()

        def my_parse_stream(stream: TextIO) -> FileInfo:
            assert_equal("file content", stream.read())
            return file_info

        with patch("dbupgrade.sql.open", mock_open(read_data="file content")):
            with patch("dbupgrade.sql.parse_sql_stream") as parse_stream:
                parse_stream.side_effect = my_parse_stream
                files = parse_sql_files(["foo", "bar"])
                assert_equal(2, len(parse_stream.call_args_list))
        assert_equal([file_info, file_info], files)

    def test_skip_files_with_parse_errors(self) -> None:
        file_info = self._create_file_info()
        with patch("dbupgrade.sql.open", mock_open(read_data="file content")):
            with patch("dbupgrade.sql.logging") as logging:
                with patch("dbupgrade.sql.parse_sql_stream") as parse_stream:
                    parse_stream.side_effect = \
                        [ParseError("test error"), file_info]
                    files = parse_sql_files(
                        [os.path.join("path", "foo"), "bar"])
                logging.warning.assert_called_once_with("foo: test error")
        assert_equal([file_info], files)


class ParseSQLStreamTest(TestCase):

    def test_all_headers(self) -> None:
        info = parse_sql_stream(StringIO("""-- Schema: my-schema
-- Dialect: sqlite
-- Version: 13
-- API-Level: 3

UPDATE foo SET bar = 99;
        """))
        assert_equal("my-schema", info.schema)
        assert_equal("sqlite", info.dialect)
        assert_equal(13, info.version)
        assert_equal(3, info.api_level)

    def test_schema_missing(self) -> None:
        with assert_raises_regex(ParseError, "missing header: schema"):
            parse_sql_stream(StringIO("""-- Dialect: sqlite
-- Version: 13
-- API-Level: 3
            """))

    def test_dialect_missing(self) -> None:
        with assert_raises_regex(ParseError, "missing header: dialect"):
            parse_sql_stream(StringIO("""-- Schema: my-schema
-- Version: 13
-- API-Level: 3
            """))

    def test_version_missing(self) -> None:
        with assert_raises_regex(ParseError, "missing header: version"):
            parse_sql_stream(StringIO("""-- Schema: my-schema
-- Dialect: sqlite
-- API-Level: 3
            """))

    def test_version_is_not_an_int(self) -> None:
        with assert_raises_regex(
                ParseError, "header is not an integer: version"):
            parse_sql_stream(StringIO("""-- Schema: my-schema
-- Dialect: sqlite
-- Version: INVALID
-- API-Level: 3
            """))

    def test_api_level_is_not_an_int(self) -> None:
        with assert_raises_regex(
                ParseError, "header is not an integer: api-level"):
            parse_sql_stream(StringIO("""-- Schema: my-schema
-- Dialect: sqlite
-- Version: 24
-- API-Level: INVALID
            """))

    def test_api_level_missing(self) -> None:
        with assert_raises_regex(ParseError, "missing header: api-level"):
            parse_sql_stream(StringIO("""-- Schema: my-schema
-- Dialect: sqlite
-- Version: 3
            """))

    def test_ignore_headers_after_break(self) -> None:
        with assert_raises_regex(ParseError, "missing header: api-level"):
            parse_sql_stream(StringIO("""-- Schema: my-schema
-- Dialect: sqlite
-- Version: 13

-- API-Level: 3
        """))
