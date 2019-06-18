from asserts import assert_equal
from io import StringIO
from typing import List

from dectest import TestCase, test

from dbupgrade.sql import split_sql


class SplitSQLTest(TestCase):
    def _call_string(self, s: str) -> List[str]:
        return list(split_sql(StringIO(s)))

    @test
    def empty_stream(self) -> None:
        statements = self._call_string("")
        assert_equal(0, len(statements))

    @test
    def one_statement(self) -> None:
        statements = self._call_string("SELECT * FROM foo;")
        assert_equal(["SELECT * FROM foo"], statements)

    @test
    def multi_line_statement(self) -> None:
        statements = self._call_string("SELECT *\nFROM foo;")
        assert_equal(["SELECT *\nFROM foo"], statements)

    @test
    def two_statements(self) -> None:
        statements = self._call_string("SELECT * FROM foo;\nDELETE FROM foo;")
        assert_equal(["SELECT * FROM foo", "DELETE FROM foo"], statements)

    @test
    def two_statements__missing_semicolon(self) -> None:
        statements = self._call_string("SELECT * FROM foo;\nDELETE FROM foo")
        assert_equal(["SELECT * FROM foo", "DELETE FROM foo"], statements)

    @test
    def double_semicolon(self) -> None:
        statements = self._call_string("SELECT * FROM foo;; DELETE FROM foo")
        assert_equal(["SELECT * FROM foo", "DELETE FROM foo"], statements)

    @test
    def full_line_comment(self) -> None:
        statements = self._call_string("-- some comment")
        assert_equal([], statements)

    @test
    def end_of_line_comment(self) -> None:
        statements = self._call_string("SELECT * -- some comment\nFROM foo;")
        assert_equal(["SELECT * FROM foo"], statements)

    @test
    def semicolon_in_string(self) -> None:
        statements = self._call_string(
            "SELECT * FROM foo WHERE t = 'foo;bar';"
        )
        assert_equal(["SELECT * FROM foo WHERE t = 'foo;bar'"], statements)

    @test
    def delimiter(self) -> None:
        statements = self._call_string(
            """ABC;
  DELIMITER $
  XXX;
  YYY;ZZZ
  $
DELIMITER ;
DEF;GHI
"""
        )
        assert_equal(["ABC", "XXX;\n  YYY;ZZZ", "DEF", "GHI"], statements)

    @test
    def delimiter_at_eol(self) -> None:
        statements = self._call_string(
            """
  DELIMITER $
  XXX;
  YYY$
DELIMITER ;
ABC
"""
        )
        assert_equal(["XXX;\n  YYY", "ABC"], statements)

    @test
    def multi_char_delimiter(self) -> None:
        statements = self._call_string(
            """ABC;
  DELIMITER $$
  XXX;
  YYY;ZZZ
  $$
DELIMITER ;
DEF;GHI
"""
        )
        assert_equal(["ABC", "XXX;\n  YYY;ZZZ", "DEF", "GHI"], statements)
