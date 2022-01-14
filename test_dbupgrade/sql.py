from typing import List

from dbupgrade.sql import split_sql


class TestSplitSQL:
    def _call_string(self, s: str) -> List[str]:
        return list(split_sql(s))

    def test_empty_stream(self) -> None:
        statements = self._call_string("")
        assert len(statements) == 0

    def test_one_statement(self) -> None:
        statements = self._call_string("SELECT * FROM foo;")
        assert statements == ["SELECT * FROM foo"]

    def test_multi_line_statement(self) -> None:
        statements = self._call_string("SELECT *\nFROM foo;")
        assert statements == ["SELECT *\nFROM foo"]

    def test_two_statements(self) -> None:
        statements = self._call_string("SELECT * FROM foo;\nDELETE FROM foo;")
        assert statements == ["SELECT * FROM foo", "DELETE FROM foo"]

    def test_two_statements__missing_semicolon(self) -> None:
        statements = self._call_string("SELECT * FROM foo;\nDELETE FROM foo")
        assert statements == ["SELECT * FROM foo", "DELETE FROM foo"]

    def test_double_semicolon(self) -> None:
        statements = self._call_string("SELECT * FROM foo;; DELETE FROM foo")
        assert statements == ["SELECT * FROM foo", "DELETE FROM foo"]

    def test_full_line_comment(self) -> None:
        statements = self._call_string("-- some comment")
        assert statements == []

    def test_end_of_line_comment(self) -> None:
        statements = self._call_string("SELECT * -- some comment\nFROM foo;")
        assert statements == ["SELECT * \nFROM foo"]

    def test_semicolon_in_string(self) -> None:
        statements = self._call_string(
            "SELECT * FROM foo WHERE t = 'foo;bar';"
        )
        assert statements == ["SELECT * FROM foo WHERE t = 'foo;bar'"]

    def test_delimiter(self) -> None:
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
        assert statements == ["ABC", "XXX;\n  YYY;ZZZ", "DEF", "GHI"]

    def test_delimiter_at_eol(self) -> None:
        statements = self._call_string(
            """
  DELIMITER $
  XXX;
  YYY$
DELIMITER ;
ABC
"""
        )
        assert statements == ["XXX;\n  YYY", "ABC"]

    def test_multi_char_delimiter(self) -> None:
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
        assert statements == ["ABC", "XXX;\n  YYY;ZZZ", "DEF", "GHI"]
