import logging
import os.path
import re
from typing import Sequence, List, Dict, IO

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


def parse_sql_stream(stream: IO[str], filename: str) -> FileInfo:
    headers = parse_sql_headers(stream)
    try:
        schema = headers["schema"]
        dialect = headers["dialect"]
        version_str = headers["version"]
        api_level_str = headers["api-level"]
    except KeyError as exc:
        raise ParseError(f"missing header: {exc.args[0]}") from None

    def to_int(string: str, header_name: str) -> int:
        try:
            return int(string)
        except ValueError:
            raise ParseError(
                f"header is not an integer: {header_name}") from None

    version = to_int(version_str, "version")
    api_level = to_int(api_level_str, "api-level")

    return FileInfo(filename, schema, dialect, version, api_level)


_line_re = re.compile(r"^--\s+((?:[a-zA-Z][a-zA-Z0-9]*)"
                      r"(?:-[a-zA-Z][a-zA-Z0-9]*)*):\s+(.*)$")


def parse_sql_headers(stream: IO[str]) -> Dict[str, str]:
    matches = []
    for line in stream:
        m = _line_re.match(line)
        if not m:
            break
        matches.append(m)
    return dict((m.group(1).lower(), m.group(2).strip()) for m in matches)
