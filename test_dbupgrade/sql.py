from asserts import assert_equal
from io import StringIO
from typing import List
from unittest import TestCase

from dbupgrade.sql import split_sql


class SplitSQLTest(TestCase):
    def _call_string(self, s: str) -> List[str]:
        return list(split_sql(StringIO(s)))

    def test_empty_stream(self) -> None:
        statements = self._call_string("")
        assert_equal(0, len(statements))

    def test_one_statement(self) -> None:
        statements = self._call_string("SELECT * FROM foo;")
        assert_equal(["SELECT * FROM foo"], statements)

    def test_multi_line_statement(self) -> None:
        statements = self._call_string("SELECT *\nFROM foo;")
        assert_equal(["SELECT *\nFROM foo"], statements)

    def test_two_statements(self) -> None:
        statements = self._call_string("SELECT * FROM foo;\nDELETE FROM foo;")
        assert_equal(["SELECT * FROM foo", "DELETE FROM foo"], statements)

    def test_two_statements__missing_semicolon(self) -> None:
        statements = self._call_string("SELECT * FROM foo;\nDELETE FROM foo")
        assert_equal(["SELECT * FROM foo", "DELETE FROM foo"], statements)

    def test_double_semicolon(self) -> None:
        statements = self._call_string("SELECT * FROM foo;; DELETE FROM foo")
        assert_equal(["SELECT * FROM foo", "DELETE FROM foo"], statements)

    def test_full_line_comment(self) -> None:
        statements = self._call_string("-- some comment")
        assert_equal([], statements)

    def test_end_of_line_comment(self) -> None:
        statements = self._call_string("SELECT * -- some comment\nFROM foo;")
        assert_equal(["SELECT * FROM foo"], statements)

    def test_semicolon_in_string(self) -> None:
        statements = self._call_string(
            "SELECT * FROM foo WHERE t = 'foo;bar';")
        assert_equal(["SELECT * FROM foo WHERE t = 'foo;bar'"], statements)

    def test_delimiter(self) -> None:
        statements = self._call_string("""ABC;
  DELIMITER $
  XXX;
  YYY;ZZZ
  $
DELIMITER ;
DEF;GHI
""")
        assert_equal(["ABC", "XXX;\n  YYY;ZZZ", "DEF", "GHI"], statements)

    def test_delimiter_at_eol(self) -> None:
        statements = self._call_string("""
  DELIMITER $
  XXX;
  YYY$
DELIMITER ;
ABC
""")
        assert_equal(["XXX;\n  YYY", "ABC"], statements)

    def test_multi_char_delimiter(self) -> None:
        statements = self._call_string("""ABC;
  DELIMITER $$
  XXX;
  YYY;ZZZ
  $$
DELIMITER ;
DEF;GHI
""")
        assert_equal(["ABC", "XXX;\n  YYY;ZZZ", "DEF", "GHI"], statements)
