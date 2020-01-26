import logging
import os.path
import re
from typing import Dict, Iterable, List, Sequence

from dbupgrade.files import FileInfo


class ParseError(Exception):
    pass


def parse_sql_files(files: Sequence[str]) -> List[FileInfo]:
    file_infos = []
    for fn in files:
        try:
            file_infos.append(_parse_sql_file(fn))
        except ParseError as exc:
            logging.warning(os.path.basename(fn) + ": " + str(exc))
    return file_infos


def _parse_sql_file(filename: str) -> FileInfo:
    with open(filename, "r") as stream:
        return parse_sql_stream(stream, filename)


def parse_sql_stream(stream: Iterable[str], filename: str) -> FileInfo:
    headers = _parse_sql_headers(stream)
    try:
        schema = headers["schema"]
        dialect = headers["dialect"]
        version = _int_header(headers, "version")
        api_level = _int_header(headers, "api-level")
    except KeyError as exc:
        raise ParseError("missing header: {0.args[0]}".format(exc)) from None

    info = FileInfo(filename, schema, dialect, version, api_level)
    if "transaction" in headers:
        info.transaction = _bool_header(headers, "transaction")
    return info


_line_re = re.compile(
    r"^--\s+((?:[a-zA-Z][a-zA-Z0-9]*)" r"(?:-[a-zA-Z][a-zA-Z0-9]*)*):\s+(.*)$"
)


def _parse_sql_headers(stream: Iterable[str]) -> Dict[str, str]:
    matches = []
    for line in stream:
        m = _line_re.match(line)
        if not m:
            break
        matches.append(m)
    return dict((m.group(1).lower(), m.group(2).strip()) for m in matches)


def _bool_header(headers: Dict[str, str], header_name: str) -> bool:
    _BOOL_VALUES = {"yes": True, "no": False}

    try:
        return _BOOL_VALUES[headers[header_name]]
    except KeyError:
        raise ParseError(
            "header must be 'yes' or 'no': " + header_name
        ) from None


def _int_header(headers: Dict[str, str], header_name: str) -> int:
    try:
        return int(headers[header_name])
    except ValueError:
        raise ParseError("header is not an integer: " + header_name) from None
