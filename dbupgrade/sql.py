import re
from typing import List

import sqlparse

_SQL_DELIMITER = ";"
_SQL_COMMENT_RE = re.compile(r"(--(| .*))$")
_SQL_DELIMITER_RE = re.compile(r"^\s*delimiter\s*(.+)$", re.IGNORECASE)
_PLACEHOLDER = "\ufffc"


def split_sql(sql: str) -> List[str]:
    """Return an iterator over the SQL statements in a stream.

    >>> list(split_sql("SELECT * FROM foo; DELETE FROM foo;"))
    ... ['SELECT * FROM foo', 'DELETE FROM foo']
    >>>

    """
    escaped = _escape_delimiters(sql)
    stmts = sqlparse.split(escaped)
    unescaped = [_unescape_delimiters(s) for s in stmts]
    processed = [_process_statement(s) for s in unescaped]
    return [s for s in processed if s.strip()]


def _escape_delimiters(sql: str) -> str:
    if _PLACEHOLDER in sql:
        raise ValueError("unexpected placeholder value in SQL string")
    new_lines: List[str] = []
    delimiter = ""
    for line in sql.splitlines():
        m = _SQL_DELIMITER_RE.match(line)
        if m:
            if m.group(1) == _SQL_DELIMITER:
                delimiter = ""
            else:
                delimiter = m.group(1)
        else:
            if delimiter:
                line = line.replace(_SQL_DELIMITER, _PLACEHOLDER)
                line = line.replace(delimiter, ";")
            new_lines.append(line)
    return "\n".join(new_lines)


def _unescape_delimiters(stmt: str) -> str:
    return stmt.replace(_PLACEHOLDER, _SQL_DELIMITER)


def _process_statement(stmt: str) -> str:
    stmt = stmt.rstrip(";")
    lines = [_remove_comment(line) for line in stmt.splitlines()]
    return "\n".join(lines).strip()


def _remove_comment(line: str) -> str:
    m = _SQL_COMMENT_RE.search(line)
    if m:
        return line[: -len(m.group(1))]
    else:
        return line
